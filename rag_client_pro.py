import argparse
import json
import socket
import sys
import time
from typing import Dict
from urllib.parse import urlparse

import requests


def safe_text(text) -> str:
    if text is None:
        return ""
    return str(text).encode("utf-8", "replace").decode("utf-8", "replace")


class RAGClientPro:
    def __init__(
        self,
        server_url: str,
        timeout: int = 180,
        max_retries: int = 3,
        retry_backoff: float = 1.5
    ):
        server_url = safe_text(server_url).strip().strip("`'\"")
        self.server_url = server_url.rstrip("/")
        if self.server_url and not self.server_url.startswith(("http://", "https://")):
            self.server_url = f"http://{self.server_url}"
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_backoff = retry_backoff
        self.health_endpoint = f"{self.server_url}/health"
        self.query_endpoint = f"{self.server_url}/query"
        self.stream_endpoint = f"{self.server_url}/query/stream"
        self.http = requests.Session()

    def probe_tcp(self, timeout: int = 3) -> Dict:
        parsed = urlparse(self.server_url)
        host = parsed.hostname
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
        if not host:
            return {"ok": False, "host": "", "port": port, "message": "无效的服务地址"}
        try:
            with socket.create_connection((host, port), timeout=timeout):
                return {"ok": True, "host": host, "port": port, "message": "TCP 可连通"}
        except Exception as e:
            return {"ok": False, "host": host, "port": port, "message": safe_text(e)}

    def check_health(self) -> Dict:
        try:
            resp = self.http.get(self.health_endpoint, timeout=8)
            resp.raise_for_status()
            data = resp.json()
            if "status" not in data:
                data["status"] = "unknown"
            return data
        except Exception as e:
            return {"status": "error", "message": safe_text(e)}

    def _post_with_retry(self, url: str, payload: Dict, stream: bool = False):
        last_err = None
        for i in range(self.max_retries):
            try:
                resp = self.http.post(url, json=payload, timeout=self.timeout, stream=stream)
                resp.raise_for_status()
                return resp
            except Exception as e:
                response = getattr(e, "response", None)
                if response is not None and 400 <= response.status_code < 500:
                    raise e
                last_err = e
                if i < self.max_retries - 1:
                    time.sleep(self.retry_backoff ** i)
        raise last_err

    def query(self, question: str, top_k: int = 12, rerank_top_n: int = 7) -> Dict:
        payload = {
            "question": safe_text(question),
            "top_k": int(top_k),
            "rerank_top_n": int(rerank_top_n)
        }
        try:
            resp = self._post_with_retry(self.query_endpoint, payload, stream=False)
            data = resp.json()
            if "success" not in data:
                data["success"] = True
            if "answer" not in data:
                data["answer"] = ""
            return data
        except Exception as e:
            return {"success": False, "answer": "", "error": safe_text(e)}

    def query_stream(self, question: str, top_k: int = 12, rerank_top_n: int = 7) -> Dict:
        payload = {
            "question": safe_text(question),
            "top_k": int(top_k),
            "rerank_top_n": int(rerank_top_n)
        }
        try:
            resp = self._post_with_retry(self.stream_endpoint, payload, stream=True)
            answer_parts = []
            for raw_line in resp.iter_lines(decode_unicode=True):
                if not raw_line:
                    continue
                line = safe_text(raw_line).strip()
                if line.startswith("data:"):
                    line = line[5:].strip()
                try:
                    obj = json.loads(line)
                except Exception:
                    print(safe_text(line), end="", flush=True)
                    answer_parts.append(safe_text(line))
                    continue
                token = safe_text(obj.get("token", ""))
                if token:
                    print(token, end="", flush=True)
                    answer_parts.append(token)
                if obj.get("done") is True:
                    break
            print()
            final_answer = "".join(answer_parts).strip()
            return {"success": True, "answer": final_answer, "error": ""}
        except Exception as e:
            err_text = safe_text(e).lower()
            if "404" in err_text or "not found" in err_text:
                return self.query(question, top_k=top_k, rerank_top_n=rerank_top_n)
            return self.query(question, top_k=top_k, rerank_top_n=rerank_top_n)


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    parser = argparse.ArgumentParser()
    parser.add_argument("server_url", nargs="?", default="http://127.0.0.1:8001")
    parser.add_argument("--question", default="")
    parser.add_argument("--stream", action="store_true")
    parser.add_argument("--health-only", action="store_true")
    parser.add_argument("--top-k", type=int, default=12)
    parser.add_argument("--rerank-top-n", type=int, default=7)
    parser.add_argument("--interactive", action="store_true")
    parser.add_argument("--skip-health", action="store_true")
    parser.add_argument("--wait-ready", type=int, default=0, help="等待服务就绪秒数，0 表示不等待")
    parser.add_argument("--probe-only", action="store_true")
    args = parser.parse_args()

    client = RAGClientPro(server_url=args.server_url)
    print(f"正在连接 RAG 服务: {client.server_url}")
    probe = client.probe_tcp()
    print(f"TCP 探测: {probe}")
    if args.probe_only:
        return

    health = client.check_health()
    print(f"服务状态: {health}")

    if args.health_only:
        return

    if health.get("status") != "ok" and args.wait_ready > 0:
        deadline = time.time() + args.wait_ready
        while time.time() < deadline:
            time.sleep(3)
            health = client.check_health()
            print(f"等待就绪中... {health}")
            if health.get("status") == "ok":
                break

    if health.get("status") != "ok" and not args.skip_health:
        message = safe_text(health.get("message", ""))
        if "timed out" in message.lower() or "refused" in message.lower():
            print("服务未就绪：网络不可达，请检查公网端口放行/映射。")
        elif health.get("status") == "initializing":
            print("服务未就绪：模型仍在初始化，可使用 --wait-ready 600 自动等待。")
        else:
            print("服务未就绪，请稍后再试")
        return

    if health.get("status") != "ok" and args.skip_health:
        print("已跳过健康检查，直接发起 query。")

    if args.interactive and not args.question:
        print("\nDeepSeek RAG 客户端已就绪，输入 exit 或 quit 退出。")
        while True:
            try:
                user_input = input("用户 >> ").strip()
                if user_input.lower() in {"exit", "quit", "退出"}:
                    print("再见！")
                    break
                if not user_input:
                    continue
                print("\n粒术 >> ", end="", flush=True)
                result = client.query_stream(user_input, top_k=args.top_k, rerank_top_n=args.rerank_top_n) if args.stream else client.query(user_input, top_k=args.top_k, rerank_top_n=args.rerank_top_n)
                if args.stream:
                    if not result.get("success"):
                        print(f"抱歉，处理请求时出错: {safe_text(result.get('error', '未知错误'))}")
                else:
                    if result.get("success"):
                        print(safe_text(result.get("answer", "")))
                    else:
                        print(f"抱歉，处理请求时出错: {safe_text(result.get('error', '未知错误'))}")
                print()
            except KeyboardInterrupt:
                print("\n再见！")
                break
            except Exception as e:
                print(f"\n错误: {safe_text(e)}\n")
        return

    if not args.question:
        print("未提供 --question，健康检查已完成。")
        return

    print("\n粒术 >> ", end="", flush=True)
    result = client.query_stream(args.question, top_k=args.top_k, rerank_top_n=args.rerank_top_n) if args.stream else client.query(args.question, top_k=args.top_k, rerank_top_n=args.rerank_top_n)
    if not args.stream:
        if result.get("success"):
            print(safe_text(result.get("answer", "")))
        else:
            print(f"抱歉，处理请求时出错: {safe_text(result.get('error', '未知错误'))}")


if __name__ == "__main__":
    main()
