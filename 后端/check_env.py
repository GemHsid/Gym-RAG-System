import sys
import os
import time


def check_package(package_name, import_name=None):
    if not import_name:
        import_name = package_name
    try:
        __import__(import_name)
        print(f"    [OK] {package_name} 已安装")
        return True
    except ImportError:
        print(f"    [X] 缺少库: {package_name} (请运行 pip install {package_name})")
        return False


def check_openai_key():
    print("[*] 检查 API KEY 配置...")
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        pass
    # 检查环境变量，LlamaIndex 默认依赖这个，或者你自己定义的其他 Key
    key = os.getenv("OPENAI_API_KEY")
    if key:
        print(f"    [OK] OPENAI_API_KEY 已检测到 ({key[:5]}...)")
    else:
        print("    [!] 警告: 未检测到 OPENAI_API_KEY 环境变量。确保你在 Django settings 或 .env 中配置了它。")


def test_llamaindex_core():
    print("\n[*] 测试 LlamaIndex 核心功能...")
    try:
        from llama_index.core import Document, VectorStoreIndex
        from llama_index.core.node_parser import SentenceSplitter

        # 1. 模拟一个小文档
        print("    -> 创建模拟文档对象...")
        text = "Django 是一个高级 Python Web 框架。TRAE 是一个强大的 AI IDE。"
        doc = Document(text=text)

        # 2. 尝试构建索引 (这会测试 Embedding 连接，需要联网)
        print("    -> 尝试构建 VectorStoreIndex (需要连接 OpenAI/Embedding API)...")
        start = time.time()
        # 注意：如果不指定 embed_model，默认会用 OpenAI。如果你用了本地模型，这里需要改。
        index = VectorStoreIndex.from_documents([doc])
        cost = time.time() - start
        print(f"    [OK] 索引构建成功，耗时 {cost:.2f}s")

        # 3. 简单检索
        print("    -> 测试检索...")
        query_engine = index.as_query_engine()
        response = query_engine.query("TRAE 是什么？")
        print(f"    [OK] 回答成功: {str(response)}")

        return True
    except Exception as e:
        print(f"    [X] LlamaIndex 测试失败: {e}")
        print("        提示: 检查网络、API Key 或 OpenAI 余额。")
        return False


if __name__ == "__main__":
    print("=== LlamaIndex RAG 环境自检 ===\n")

    # 1. 检查依赖
    deps = [
        ("django", "django"),
        ("llama-index", "llama_index"),
        ("openai", "openai"),
        ("python-dotenv", "dotenv"),  # 建议用来管理环境变量
    ]

    all_installed = True
    for pkg, imp in deps:
        if not check_package(pkg, imp):
            all_installed = False

    check_openai_key()

    # 2. 如果依赖都齐了，跑功能测试
    if all_installed:
        test_llamaindex_core()

    print("\n=== 检查结束 ===")
