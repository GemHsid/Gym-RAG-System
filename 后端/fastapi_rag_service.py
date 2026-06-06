import asyncio
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any


PRIVATE_LIB = "/data/llama_libs"
if PRIVATE_LIB not in os.sys.path:
    os.sys.path.insert(0, PRIVATE_LIB)
    
import nest_asyncio
import torch
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from llama_index.core import (
    Document,
    PromptTemplate,
    Settings,
    SimpleDirectoryReader,
    StorageContext,
    VectorStoreIndex,
)
from llama_index.core.node_parser import HierarchicalNodeParser, get_leaf_nodes
from llama_index.core.postprocessor import LLMRerank
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import QueryFusionRetriever, RecursiveRetriever
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openai_like import OpenAILike
from llama_index.retrievers.bm25 import BM25Retriever
from llama_index.vector_stores.milvus import MilvusVectorStore



nest_asyncio.apply()


PROJECT_DIR = Path(__file__).resolve().parent
DEFAULT_DATA_DIR = PROJECT_DIR / "data" / "rag_markdown_knowledge"
DEFAULT_VECTOR_DB = PROJECT_DIR / "advanced_rag_fitness.db"

DATA_DIR = Path(os.getenv("RAG_DATA_DIR", str(DEFAULT_DATA_DIR)))
EMBED_PATH = os.getenv("RAG_EMBED_PATH", "/mnt/moark-models/Qwen3-Embedding-8B")
LLM_MODEL = os.getenv("RAG_LLM_MODEL", "Qwen3-8B")
LLM_API_BASE = os.getenv("RAG_LLM_API_BASE", "https://1q1z8id7fiwt5g4u.apps.gitee-ai.com:32481/v1")
SERVER_HOST = os.getenv("RAG_SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("RAG_SERVER_PORT", "8080"))
TOP_K = int(os.getenv("RAG_TOP_K", "3"))
VECTOR_DIM = int(os.getenv("RAG_VECTOR_DIM", "4096"))


class QueryRequest(BaseModel):
    query: str | None = None
    question: str | None = None
    top_k: int = Field(default=TOP_K, ge=1, le=10)
    k: int | None = Field(default=None, ge=1, le=10)
    need_sources: bool = True
    need_related_questions: bool = True
    session_meta: dict[str, Any] | None = None


class QueryResponse(BaseModel):
    answer: str
    context: str = ""
    sources: list[str] = []
    related_questions: list[str] = []


def clean_document_content(documents):
    print(f">>> 正在清洗 {len(documents)} 篇健身房知识库文档的 Unicode 编码...")
    cleaned_docs = []
    for doc in documents:
        original_text = doc.get_content() or ""
        if not original_text:
            continue
        cleaned_text = original_text.encode("utf-8", "ignore").decode("utf-8")
        cleaned_docs.append(
            Document(
                text=cleaned_text,
                metadata=doc.metadata or {},
                excluded_embed_metadata_keys=doc.excluded_embed_metadata_keys or [],
                excluded_llm_metadata_keys=doc.excluded_llm_metadata_keys or [],
                id_=doc.id_,
            )
        )
    print(f">>> 清洗完成，有效文档数: {len(cleaned_docs)}")
    return cleaned_docs


def clean_think_tag(text):
    text = str(text).strip()
    if not text:
        return "当前知识库暂时没有组织出有效回答，请稍后再试一次。"
    if "</think>" in text:
        cleaned = text.split("</think>")[-1].strip()
        if cleaned:
            return cleaned
        return "当前知识库暂时没有组织出有效回答，请换个问法试试。"
    return text


def get_retrieval_strategy(user_input: str) -> int:
    vague_keywords = [
        "总结",
        "概括",
        "介绍",
        "推荐",
        "你好",
        "你是谁",
        "有什么",
        "怎么收费",
        "怎么练",
    ]
    if len(user_input) < 10 or any(keyword in user_input for keyword in vague_keywords):
        return 1
    return 3


def is_greeting(user_input: str) -> bool:
    text = user_input.lower()
    greetings = ["你好", "嗨", "hello", "你是谁", "早安", "午安", "在吗", "小助手", "铁馆"]
    return any(token in text for token in greetings) or len(user_input.strip()) < 5


def build_related_questions(query: str) -> list[str]:
    candidates = []
    if any(word in query for word in ["会员", "月卡", "年卡", "价格", "退款"]):
        candidates.extend(
            [
                "会员卡有哪些，分别多少钱？",
                "买卡后多久生效？",
                "退款规则是怎样的？",
            ]
        )
    if any(word in query for word in ["课程", "预约", "教练"]):
        candidates.extend(
            [
                "今天有哪些课程？",
                "新手适合预约什么课程？",
                "课程迟到还能进吗？",
            ]
        )
    if any(word in query for word in ["器械", "跑步机", "史密斯", "深蹲"]):
        candidates.extend(
            [
                "史密斯机适合新手吗？",
                "跑步机在什么区域？",
                "器械坏了怎么报修？",
            ]
        )
    if any(word in query for word in ["营业", "时间", "洗澡", "停车", "wifi"]):
        candidates.extend(
            [
                "健身房是 24 小时营业吗？",
                "有洗澡和更衣室吗？",
                "Wi-Fi 密码是多少？",
            ]
        )
    if not candidates:
        candidates.extend(
            [
                "会员卡有哪些？",
                "今天有什么课？",
                "史密斯机怎么用？",
            ]
        )
    # 去重并保序
    result = []
    for item in candidates:
        if item not in result:
            result.append(item)
    return result[:3]


class GymRAGService:
    def __init__(self):
        self.ready = False
        self.query_engine = None
        self.fusion_retriever = None
        self.init_error = ""

    def initialize(self):
        if self.ready:
            return

        print(">>> 正在初始化健身房 RAG FastAPI 服务...")
        print(f">>> 知识库目录: {DATA_DIR}")
        print(f">>> 向量模型路径: {EMBED_PATH}")
        print(f">>> 文本模型地址: {LLM_API_BASE}")

        if not DATA_DIR.exists():
            raise FileNotFoundError(f"知识库目录不存在: {DATA_DIR}")

        Settings.embed_model = HuggingFaceEmbedding(
            model_name=EMBED_PATH,
            device="cuda",
            trust_remote_code=True,
            model_kwargs={"torch_dtype": torch.float16},
        )
        Settings.llm = OpenAILike(
            model=LLM_MODEL,
            api_base=LLM_API_BASE,
            api_key="fake",
            is_chat_model=True,
            timeout=120.0,
        )

        reader = SimpleDirectoryReader(input_dir=str(DATA_DIR), recursive=True)
        raw_documents = reader.load_data()
        documents = clean_document_content(raw_documents)

        node_parser = HierarchicalNodeParser.from_defaults(chunk_sizes=[1536, 512, 256])
        all_nodes = node_parser.get_nodes_from_documents(documents)
        raw_leaf_nodes = get_leaf_nodes(all_nodes)

        leaf_nodes = []
        for node in raw_leaf_nodes:
            text_content = node.get_content()
            if not isinstance(text_content, str):
                continue
            clean_text = text_content.encode("utf-8", "ignore").decode("utf-8").strip()
            if not clean_text:
                continue
            node.text = clean_text
            leaf_nodes.append(node)

        print(f">>> 深度过滤完成，有效叶子节点: {len(leaf_nodes)} / 原始: {len(raw_leaf_nodes)}")

        vector_store = MilvusVectorStore(
            uri=str(DEFAULT_VECTOR_DB),
            dim=VECTOR_DIM,
            overwrite=True,
        )
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        storage_context.docstore.add_documents(all_nodes)

        index = VectorStoreIndex(leaf_nodes, storage_context=storage_context, show_progress=True)
        vector_retriever = index.as_retriever(similarity_top_k=12)
        bm25_retriever = BM25Retriever.from_defaults(nodes=leaf_nodes, similarity_top_k=12)

        self.fusion_retriever = QueryFusionRetriever(
            [vector_retriever, bm25_retriever],
            similarity_top_k=12,
            num_queries=1,
            mode="reciprocal_rerank",
            use_async=False,
        )

        recursive_retriever = RecursiveRetriever(
            "vector",
            retriever_dict={"vector": self.fusion_retriever},
            node_dict={node.node_id: node for node in all_nodes},
        )

        reranker = LLMRerank(llm=Settings.llm, choice_batch_size=15, top_n=7)

        qa_prompt_tmpl = PromptTemplate(
            "【身份设定】你是美式铁馆智能健身中心的 RAG 知识库 AI 助手，名字叫“铁馆小助手”。"
            "你负责回答场馆营业服务、会员卡、课程预约、器械使用、训练建议等问题。\n\n"
            "【场景 A：社交寒暄】\n"
            "如果用户只是在打招呼，或者问你是谁，请忽略参考资料，直接用温暖、专业、简洁的口吻回复，"
            "并说明你可以解答健身房相关问题。\n\n"
            "【场景 B：场馆业务与健身咨询】\n"
            "如果用户在询问营业时间、地址、停车、Wi-Fi、会员卡价格、退款规则、课程安排、"
            "教练信息、器械位置、动作建议等问题，请优先根据下方知识库资料回答：\n"
            "参考资料：\n---------------------\n{context_str}\n---------------------\n"
            "回答准则：\n"
            "1. 优先依据知识库内容回答，不允许编造具体的场馆制度、价格、课程安排。\n"
            "2. 如果知识库没有明确提到，请礼貌说明“当前知识库里暂时没有这条明确信息”。\n"
            "3. 若涉及训练建议，可以给出基础建议，但不能替代医疗诊断、康复处方或药物建议。\n"
            "4. 保持条理清晰、语气友好，适度体现专业度。\n\n"
            "用户提问：{query_str}\n"
        )

        self.query_engine = RetrieverQueryEngine.from_args(
            retriever=recursive_retriever,
            node_postprocessors=[reranker],
            text_qa_template=qa_prompt_tmpl,
        )
        self.ready = True
        print(">>> 健身房 RAG FastAPI 服务已就绪")

    def query(self, user_input: str, top_k: int = TOP_K, need_sources: bool = True, need_related_questions: bool = True):
        if not self.ready:
            self.initialize()

        if self.fusion_retriever:
            self.fusion_retriever.num_queries = get_retrieval_strategy(user_input)

        if is_greeting(user_input):
            prompt = (
                "你是美式铁馆智能健身中心的智能助手“铁馆小助手”。"
                "请用温暖、专业、简洁的口吻回应用户问候，并明确告诉用户："
                "你可以帮助解答营业时间、会员卡、课程预约、器械使用和基础训练建议等问题。"
            )
            result = Settings.llm.complete(f"{prompt}\n用户输入：{user_input}")
            answer = clean_think_tag(result.text)
            return {
                "answer": answer,
                "context": "",
                "sources": [],
                "related_questions": build_related_questions(user_input) if need_related_questions else [],
            }

        response = self.query_engine.query(user_input)
        answer = clean_think_tag(response.response)

        source_nodes = getattr(response, "source_nodes", []) or []
        context_blocks = []
        sources = []
        for idx, source in enumerate(source_nodes[:top_k], start=1):
            node = getattr(source, "node", None)
            if node is None:
                continue
            content = (node.get_content() or "").strip()
            if content:
                context_blocks.append(content)
            metadata = getattr(node, "metadata", {}) or {}
            source_name = metadata.get("file_name") or metadata.get("filename") or metadata.get("source")
            if source_name:
                sources.append(str(source_name))
            elif content:
                sources.append(f"知识片段{idx}")

        context = "\n\n".join(context_blocks[:top_k])

        if not answer or len(answer) < 5:
            answer = "当前知识库暂时没有检索到足够准确的信息。你可以换个更具体的问法继续提问。"

        return {
            "answer": answer,
            "context": context,
            "sources": sources if need_sources else [],
            "related_questions": build_related_questions(user_input) if need_related_questions else [],
        }


service = GymRAGService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        # MilvusVectorStore 会在初始化阶段依赖当前线程已有 event loop，
        # 因此这里不能放进线程池，否则会报 "no running event loop"。
        service.initialize()
    except Exception as exc:
        service.init_error = str(exc)
        print(f">>> 服务启动时初始化失败: {exc}")
    yield


app = FastAPI(title="Gym RAG FastAPI Service", version="1.0.0", lifespan=lifespan)


@app.get("/")
async def root():
    return {
        "service": "gym-rag-fastapi",
        "port": SERVER_PORT,
        "llm_api_base": LLM_API_BASE,
        "model": LLM_MODEL,
        "data_dir": str(DATA_DIR),
    }


@app.get("/health")
async def health():
    return {
        "status": "ok" if service.ready else "initializing",
        "ready": service.ready,
        "llm_api_base": LLM_API_BASE,
        "model": LLM_MODEL,
        "data_dir": str(DATA_DIR),
        "error": service.init_error,
    }


async def handle_query(payload: QueryRequest):
    query_text = (payload.query or payload.question or "").strip()
    if not query_text:
        raise HTTPException(status_code=400, detail="缺少 query 或 question")

    top_k = payload.k or payload.top_k or TOP_K

    try:
        # 查询阶段同样保持在应用主事件循环线程内执行，避免底层向量库
        # 在工作线程中再次触发 "no running event loop"。
        result = service.query(
            user_input=query_text,
            top_k=top_k,
            need_sources=payload.need_sources,
            need_related_questions=payload.need_related_questions,
        )
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"RAG 服务处理失败: {exc}") from exc


@app.post("/query", response_model=QueryResponse)
async def query_endpoint(payload: QueryRequest):
    return await handle_query(payload)


@app.post("/rag/search", response_model=QueryResponse)
async def rag_search_endpoint(payload: QueryRequest):
    return await handle_query(payload)


if __name__ == "__main__":
    uvicorn.run(
        app,
        host=SERVER_HOST,
        port=SERVER_PORT,
        reload=False,
    )
