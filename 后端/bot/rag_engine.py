import os
import requests
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

class RAGEngine:
    def __init__(self):
        self.vector_store = None
        # 设置国内 HF 镜像，防止下载超时或找不到文件
        os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
        try:
            self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
            self.initialize_knowledge_base()
        except Exception as e:
            print(f"RAG Engine Initialization Error: {e}")
            self.embeddings = None
        
    def initialize_knowledge_base(self):
        """初始化本地知识库"""
        kb_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'knowledge.txt')
        
        if not os.path.exists(kb_path):
            print(f"Warning: 知识库文件未找到 {kb_path}")
            return
            
        # 1. 加载文档
        loader = TextLoader(kb_path, encoding='utf-8')
        documents = loader.load()
        
        # 2. 文本切分
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=200,
            chunk_overlap=50,
            separators=["\n\n", "\n", "。", "！", "？", "，", "、", ""]
        )
        texts = text_splitter.split_documents(documents)
        
        # 3. 向量化并存储到 FAISS
        self.vector_store = FAISS.from_documents(texts, self.embeddings)
        print("✅ 本地知识库加载并向量化完成")

    def retrieve(self, query: str, top_k: int = 3):
        """检索相关知识"""
        if not self.vector_store or not self.embeddings:
            # 降级：如果向量模型没加载成功，尝试做简单的字符串匹配
            try:
                kb_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'knowledge.txt')
                with open(kb_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if query in content or any(word in content for word in query.split()):
                        return content[:300] + "..." # 截取部分返回
            except Exception:
                pass
            return ""
            
        docs = self.vector_store.similarity_search(query, k=top_k)
        context = "\n".join([doc.page_content for doc in docs])
        return context

    def chat(self, user_message: str):
        """与大模型对话"""
        # 1. 从本地向量库检索上下文
        context = self.retrieve(user_message)
        
        # 2. 构建 Prompt
        prompt = f"""你是一个名为“Trae”的智能健身房AI私教和客服。请根据以下提供的健身房内部规定或资料，简明扼要地回答用户的问题。如果资料中没有相关信息，请利用你的通用健身知识回答，但必须保持礼貌和专业。

【参考资料】
{context if context else '无相关内部资料。'}

【用户问题】
{user_message}

【你的回答】
"""

        # 3. 调用云端大模型 API (这里以 DeepSeek / 任何兼容 OpenAI 格式的 API 为例)
        api_key = os.environ.get("LLM_API_KEY", "")
        base_url = os.environ.get("LLM_BASE_URL", "https://api.deepseek.com/v1")
        model = os.environ.get("LLM_MODEL", "deepseek-chat")
        
        if not api_key:
            return "【系统提示】大模型 API Key 未配置，无法进行推理。请在 .env 中配置 LLM_API_KEY。这里是本地检索到的相关信息：\n" + (context if context else "未检索到信息。")
            
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": [
                {"role": "system", "content": "你是一个专业的健身房AI客服。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        try:
            response = requests.post(f"{base_url}/chat/completions", headers=headers, json=data, timeout=15)
            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content'].strip()
        except Exception as e:
            return f"抱歉，AI 引擎开小差了，请稍后再试。(错误: {str(e)})"

# 使用懒加载模式导出单例，避免 Django 启动时阻塞下载
_rag_engine_instance = None

def get_rag_engine():
    global _rag_engine_instance
    if _rag_engine_instance is None:
        _rag_engine_instance = RAGEngine()
    return _rag_engine_instance