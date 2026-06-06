import os
import requests
from django.conf import settings
from openai import OpenAI
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from drf_spectacular.utils import extend_schema, inline_serializer
from .models import ChatSession, ChatMessage
from common.api import ok, fail
from common.demo_content import build_ai_content, build_home_content, build_order_content
 


def _extract_rag_context(payload):
    if payload is None:
        return ""
    if isinstance(payload, str):
        return payload
    if isinstance(payload, dict):
        for key in ("context", "retrieved_context", "text", "result"):
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        data = payload.get("data")
        if isinstance(data, dict):
            for key in ("context", "retrieved_context", "text", "result"):
                value = data.get(key)
                if isinstance(value, str) and value.strip():
                    return value.strip()
    return ""


def _extract_rag_answer(payload):
    if payload is None:
        return ""
    if isinstance(payload, str):
        return payload.strip()
    if isinstance(payload, dict):
        for key in ("answer", "response", "content"):
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        data = payload.get("data")
        if isinstance(data, dict):
            for key in ("answer", "response", "content"):
                value = data.get(key)
                if isinstance(value, str) and value.strip():
                    return value.strip()
    return ""


def _extract_rag_list(payload, key):
    if payload is None:
        return []
    if isinstance(payload, dict):
        value = payload.get(key)
        if isinstance(value, list):
            return value
        data = payload.get("data")
        if isinstance(data, dict):
            value = data.get(key)
            if isinstance(value, list):
                return value
    return []


def _build_rag_candidate_urls(url: str):
    normalized = (url or "").strip().rstrip("/")
    if not normalized:
        return []
    candidates = []
    if normalized.endswith("/query"):
        base = normalized[: -len("/query")]
        candidates = [
            normalized,
            f"{normalized}/",
            f"{base}/rag/search",
            f"{base}/rag/search/",
        ]
    elif normalized.endswith("/rag/search"):
        base = normalized[: -len("/rag/search")]
        candidates = [
            normalized,
            f"{normalized}/",
            f"{base}/query",
            f"{base}/query/",
        ]
    else:
        candidates = [
            f"{normalized}/rag/search",
            f"{normalized}/rag/search/",
            f"{normalized}/query",
            f"{normalized}/query/",
            normalized,
            f"{normalized}/",
        ]
    result = []
    for item in candidates:
        if item and item not in result:
            result.append(item)
    return result


def _retrieve_rag_payload(query: str, top_k: int = 3):
    url = (getattr(settings, "RAG_SERVICE_URL", "") or "").strip()
    if not url:
        return None
    timeout = max(float(getattr(settings, "RAG_SERVICE_TIMEOUT", 10.0) or 10.0), 1.0)
    last_error = ""
    for candidate in _build_rag_candidate_urls(url):
        try:
            resp = requests.post(
                candidate,
                json={"query": query, "question": query, "top_k": top_k, "k": top_k},
                timeout=timeout,
            )
            if resp.status_code >= 400:
                last_error = f"{candidate} status={resp.status_code}"
                continue
            try:
                return resp.json()
            except Exception:
                return resp.text
        except Exception as exc:
            last_error = f"{candidate} error={exc}"
            continue
    if last_error:
        return {"context": "", "answer": "", "sources": [], "related_questions": [], "error": last_error}
    return None


def _extract_rag_error(payload):
    if isinstance(payload, dict):
        error = payload.get("error")
        if isinstance(error, str):
            return error.strip()
    return ""


def _build_chat_topic(query: str):
    text = (query or "").strip()
    if not text:
        return "新的对话"
    return text[:20]

class ChatHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses=inline_serializer(
            name="ChatHistoryEnvelope",
            fields={
                "code": serializers.IntegerField(),
                "message": serializers.CharField(),
                "data": inline_serializer(
                    name="ChatHistoryList",
                    fields={
                        "id": serializers.IntegerField(),
                        "role": serializers.CharField(),
                        "content": serializers.CharField(),
                        "created_at": serializers.DateTimeField(),
                    },
                    many=True,
                ),
            },
        ),
    )
    def get(self, request):
        user = request.user
        session = ChatSession.objects.filter(user=user).first()
        if not session:
            return ok([], message="获取成功")
            
        messages = ChatMessage.objects.filter(session=session).order_by("created_at")
        data = [
            {
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.created_at,
            }
            for msg in messages
        ]
        return ok(data, message="获取成功")


class BotConfigView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses=inline_serializer(
            name="BotConfigEnvelope",
            fields={
                "code": serializers.IntegerField(),
                "message": serializers.CharField(),
                "data": serializers.DictField(),
            },
        )
    )
    def get(self, request):
        return ok(build_ai_content(), message="获取成功")


class ChatAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=inline_serializer(
            name="ChatRequest",
            fields={
                "message": serializers.CharField(required=False, allow_blank=False),
                "query": serializers.CharField(required=False, allow_blank=False),
            },
        ),
        responses=inline_serializer(
            name="ChatEnvelope",
            fields={
                "code": serializers.IntegerField(),
                "message": serializers.CharField(),
                "data": inline_serializer(
                    name="ChatData",
                    fields={
                        "answer": serializers.CharField(),
                        "context": serializers.CharField(required=False, allow_blank=True),
                        "sources": serializers.ListField(required=False),
                        "related_questions": serializers.ListField(required=False),
                    },
                ),
            },
        ),
    )
    def post(self, request):
        user = request.user
        query = (request.data.get("query") or request.data.get("message") or "").strip()

        if not query:
            return fail("缺少 query", code=400, http_status=400)

        session = ChatSession.objects.filter(user=user).first()
        latest_topic = _build_chat_topic(query)
        if not session:
            session = ChatSession.objects.create(user=user, topic=latest_topic)
        elif session.topic != latest_topic:
            session.topic = latest_topic
            session.save(update_fields=["topic"])

        ChatMessage.objects.create(session=session, role="user", content=query)

        rag_payload = _retrieve_rag_payload(query, top_k=3)
        retrieved_context = _extract_rag_context(rag_payload)
        rag_answer = _extract_rag_answer(rag_payload)
        rag_sources = _extract_rag_list(rag_payload, "sources")
        related_questions = _extract_rag_list(rag_payload, "related_questions")
        rag_error = _extract_rag_error(rag_payload)
        rag_mode = (getattr(settings, "RAG_SERVICE_MODE", "context") or "context").strip().lower()
        has_rag_context = bool(retrieved_context.strip())
        has_rag_answer = bool(rag_answer.strip())

        # 优雅降级：如果没有配置大模型 API，直接使用 Mock 回答
        api_key = (
            (getattr(settings, "LLM_API_KEY", None) or "").strip()
            or (getattr(settings, "MOLIFANGZHOU_API_KEY", None) or "").strip()
            or os.getenv("MOLIFANGZHOU_API_KEY", "")
            or os.getenv("GITEE_AI_API_KEY", "")
        )

        if has_rag_answer:
            ai_answer = rag_answer
        elif not has_rag_context:
            if rag_error:
                ai_answer = "当前知识库服务暂时不可用，未能返回有效检索结果。请稍后重试，或联系管理员检查 RAG 服务路由。"
            else:
                ai_answer = "当前知识库里暂时没有检索到与你问题直接相关的内容。请换个更具体的问法，例如补充器械名称、课程名称或会员业务关键词。"
        elif not api_key or api_key == "your_key_here":
            # 无模型密钥时，不再让系统自由发挥，只基于检索结果做保守回答
            home_content = build_home_content()
            order_content = build_order_content()
            if "营业" in query or "时间" in query:
                ai_answer = f"【本地知识库提示】{home_content['gym_name']}为{home_content['business_hours']}，门店地址是{home_content['address']}。"
            elif "器械" in query or "跑步机" in query or "史密斯" in query:
                ai_answer = "【本地知识库提示】根据检索，场馆的有氧区配备了跑步机，力量区配备了史密斯机等多种专业器械。"
            elif "收费" in query or "价格" in query or "多少钱" in query:
                ai_answer = f"【本地知识库提示】当前主推卡种包括基础月卡199元、年度VIP卡1999元。{order_content['payment_simulation_note']}"
            elif "课程" in query or "新手" in query:
                ai_answer = "【本地知识库提示】新手可优先体验新手燃脂训练课或基础体验拉伸课；有一定基础后可预约基础力量提升课。"
            else:
                ai_answer = f"【本地知识库提示】已检索到相关资料，但当前未配置模型生成服务。请结合返回的知识片段进一步查看。"
        else:
            # 2. 云端大模型推理：仅在拿到检索上下文后，基于知识库内容组织答案
            try:
                base_url = (
                    (getattr(settings, "LLM_BASE_URL", None) or "").strip()
                    or (getattr(settings, "MOLIFANGZHOU_BASE_URL", None) or "").strip()
                    or os.getenv("MOLIFANGZHOU_BASE_URL", "https://ai.gitee.com/v1")
                )
                model = (
                    (getattr(settings, "LLM_MODEL", None) or "").strip()
                    or (getattr(settings, "MOLIFANGZHOU_MODEL", None) or "").strip()
                    or os.getenv("MOLIFANGZHOU_MODEL", "MiniMax-M2.5")
                )
                
                client = OpenAI(api_key=api_key, base_url=base_url)

                history = list(
                    ChatMessage.objects.filter(session=session)
                    .order_by("-created_at")[:6]
                )[::-1]

                system_prompt = (
                    "你是美式铁馆智能健身系统的知识库问答助手。请严格依据以下【本店检索信息】回答用户。\n"
                    "要求：\n"
                    "1. 只能依据【本店检索信息】作答，不要补充检索信息中没有出现的营业时间、价格、课程安排、Wi-Fi、规则等事实。\n"
                    "2. 如果检索信息不足以支持结论，明确回复“当前知识库里暂时没有这条明确信息”。\n"
                    "3. 可以对训练动作做简要整理，但不得编造本店专属制度。\n"
                    "4. 回答尽量简洁，优先给出直接结论。\n\n"
                    f"【本店检索信息】：\n{retrieved_context}"
                )

                messages = [{"role": "system", "content": system_prompt}]
                for msg in history:
                    role = "user" if msg.role == "user" else "assistant"
                    messages.append({"role": role, "content": msg.content})

                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_tokens=384,
                    temperature=0.2,
                    stream=False
                )

                ai_answer = response.choices[0].message.content

            except Exception as e:
                ai_answer = f"抱歉，我的智能大脑开小差了 (Error: {str(e)})。请稍后再试。"

        ChatMessage.objects.create(
            session=session,
            role="ai",
            content=ai_answer,
            retrieved_context=retrieved_context,
        )
        
        return ok(
            {
                "answer": ai_answer,
                "context": retrieved_context,
                "sources": rag_sources,
                "related_questions": related_questions,
            },
            message="请求成功",
        )
