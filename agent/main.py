"""
FastAPI Agent Server
提供 HTTP API 接口供 Java 后端调用
"""

import os
from typing import Optional, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

from chatbot import ChatbotWithMemory
from langgraph_agent import LangGraphAgent
from tools import FileHandler


# 配置: 选择使用哪个 agent (默认使用LangGraph)
USE_LANGGRAPH = os.getenv("USE_LANGGRAPH", "true").lower() == "true"

# 全局 agent 实例
chatbot: Optional[ChatbotWithMemory] = None
langgraph_agent: Optional[LangGraphAgent] = None
file_handler: Optional[FileHandler] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global chatbot, langgraph_agent, file_handler
    
    # 初始化文件处理器
    file_handler = FileHandler(workspace_dir="./workspace")
    print("✅ 文件处理器初始化完成")
    
    if USE_LANGGRAPH:
        print("正在初始化 LangGraph Agent...")
        try:
            langgraph_agent = LangGraphAgent(
                memory_dir="./chat_memory_db",
                workspace_dir="./workspace"
            )
            print("✅ LangGraph Agent 初始化完成")
        except Exception as e:
            print(f"❌ 初始化失败: {e}")
            raise
    else:
        print("正在初始化 Chatbot Agent...")
        try:
            chatbot = ChatbotWithMemory(
                memory_dir="./chat_memory_db",
                short_term_limit=10,
                retrieve_memories=5
            )
            print("✅ Chatbot Agent 初始化完成")
        except Exception as e:
            print(f"❌ 初始化失败: {e}")
            raise
    
    yield
    
    print("正在关闭 Agent...")


# 创建 FastAPI 应用
app = FastAPI(
    title="Chatbot Agent API",
    description="带有长时记忆的对话机器人 Agent 服务 (支持 LangGraph)",
    version="2.0.0",
    lifespan=lifespan
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 请求/响应模型
class ChatRequest(BaseModel):
    message: str = Field(..., description="用户消息")
    session_id: str = Field(default="default", description="会话ID")
    enable_web_search: bool = Field(default=False, description="是否启用联网搜索")


class ChatResponse(BaseModel):
    response: str = Field(..., description="助手回复")
    session_id: str = Field(..., description="会话ID")


class MemoryStatsResponse(BaseModel):
    long_term_memories: int = Field(..., description="长时记忆数量")
    short_term_messages: int = Field(..., description="短时记忆消息数量")


class SummarizeRequest(BaseModel):
    text: str = Field(..., description="需要总结的文本")
    max_length: Optional[int] = Field(15, description="总结的最大长度（字数）")


class SummarizeResponse(BaseModel):
    summary: str = Field(..., description="总结结果")


class ExtractRequest(BaseModel):
    text: str = Field(..., description="需要提取信息的文本")


class ExtractResponse(BaseModel):
    extracted_info: str = Field(..., description="提取的关键信息")


class TranslateRequest(BaseModel):
    text: str = Field(..., description="需要翻译的文本")
    target_language: str = Field(default="English", description="目标语言")


class TranslateResponse(BaseModel):
    translated_text: str = Field(..., description="翻译后的文本")


class SuccessResponse(BaseModel):
    success: bool = Field(..., description="操作是否成功")
    message: str = Field(default="", description="消息")


# API 路由
@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "chatbot-agent"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    对话接口
    
    接收用户消息，返回助手回复
    支持 enable_web_search 参数强制启用联网搜索
    """
    global chatbot, langgraph_agent
    
    if USE_LANGGRAPH:
        if langgraph_agent is None:
            raise HTTPException(status_code=503, detail="LangGraph Agent not initialized")
        
        try:
            # 如果启用联网搜索，使用带搜索的方法
            if request.enable_web_search:
                response = langgraph_agent.chat_with_search(request.message)
            else:
                response = langgraph_agent.chat(request.message)
            return ChatResponse(
                response=response,
                session_id=request.session_id
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    else:
        if chatbot is None:
            raise HTTPException(status_code=503, detail="Chatbot not initialized")
        
        try:
            response = chatbot.chat(request.message)
            return ChatResponse(
                response=response,
                session_id=request.session_id
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats", response_model=MemoryStatsResponse)
async def get_stats():
    """
    获取记忆统计信息
    """
    global chatbot, langgraph_agent
    
    if USE_LANGGRAPH:
        if langgraph_agent is None:
            raise HTTPException(status_code=503, detail="LangGraph Agent not initialized")
        
        try:
            stats = langgraph_agent.get_memory_stats()
            return MemoryStatsResponse(
                long_term_memories=stats["long_term_memories"],
                short_term_messages=0  # LangGraph版本没有短期记忆统计
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    else:
        if chatbot is None:
            raise HTTPException(status_code=503, detail="Chatbot not initialized")
        
        try:
            stats = chatbot.get_memory_stats()
            return MemoryStatsResponse(
                long_term_memories=stats["long_term_memories"],
                short_term_messages=stats["short_term_messages"]
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/memory/clear-short-term", response_model=SuccessResponse)
async def clear_short_term_memory():
    """
    清除短时记忆
    """
    global chatbot
    
    if chatbot is None:
        raise HTTPException(status_code=503, detail="Chatbot not initialized")
    
    try:
        chatbot.clear_short_term_memory()
        return SuccessResponse(success=True, message="Short-term memory cleared")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/memory/clear-all", response_model=SuccessResponse)
async def clear_all_memory():
    """
    清除所有记忆
    """
    global chatbot, langgraph_agent
    
    if USE_LANGGRAPH:
        if langgraph_agent is None:
            raise HTTPException(status_code=503, detail="LangGraph Agent not initialized")
        try:
            langgraph_agent.clear_all_memory()
            return SuccessResponse(success=True, message="All memory cleared")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    else:
        if chatbot is None:
            raise HTTPException(status_code=503, detail="Chatbot not initialized")
        try:
            chatbot.clear_all_memory()
            return SuccessResponse(success=True, message="All memory cleared")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/summarize", response_model=SummarizeResponse)
async def summarize_text(request: SummarizeRequest):
    """
    文本总结接口
    
    对输入的文本进行智能总结
    """
    global chatbot, langgraph_agent
    
    if USE_LANGGRAPH:
        if langgraph_agent is None:
            raise HTTPException(status_code=503, detail="LangGraph Agent not initialized")
        try:
            summary = langgraph_agent.summarize(request.text, request.max_length)
            return SummarizeResponse(summary=summary)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    else:
        if chatbot is None:
            raise HTTPException(status_code=503, detail="Chatbot not initialized")
        try:
            summary = chatbot.summarize(request.text, request.max_length)
            return SummarizeResponse(summary=summary)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/extract", response_model=ExtractResponse)
async def extract_information(request: ExtractRequest):
    """
    信息提取接口
    
    从文本中提取关键信息
    """
    global chatbot, langgraph_agent
    
    if USE_LANGGRAPH:
        if langgraph_agent is None:
            raise HTTPException(status_code=503, detail="LangGraph Agent not initialized")
        try:
            extracted = langgraph_agent.extract_information(request.text)
            return ExtractResponse(extracted_info=extracted)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    else:
        if chatbot is None:
            raise HTTPException(status_code=503, detail="Chatbot not initialized")
        try:
            extracted = chatbot.extract_information(request.text)
            return ExtractResponse(extracted_info=extracted)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/translate", response_model=TranslateResponse)
async def translate_text(request: TranslateRequest):
    """
    翻译接口
    
    将文本翻译成指定语言
    """
    global chatbot, langgraph_agent
    
    if USE_LANGGRAPH:
        if langgraph_agent is None:
            raise HTTPException(status_code=503, detail="LangGraph Agent not initialized")
        try:
            translated = langgraph_agent.translate(request.text, request.target_language)
            return TranslateResponse(translated_text=translated)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    else:
        if chatbot is None:
            raise HTTPException(status_code=503, detail="Chatbot not initialized")
        try:
            translated = chatbot.translate(request.text, request.target_language)
            return TranslateResponse(translated_text=translated)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


# 文件上传响应模型
class FileUploadResponse(BaseModel):
    success: bool
    filename: str = ""
    original_name: str = ""
    filepath: str = ""
    size: int = 0
    error: str = ""


class FileAnalyzeRequest(BaseModel):
    filepath: str = Field(..., description="文件路径")
    question: str = Field(default="请分析这个文件的内容", description="关于文件的问题")


class FileAnalyzeResponse(BaseModel):
    success: bool
    analysis: str = ""
    file_type: str = ""
    error: str = ""


@app.post("/api/upload", response_model=FileUploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    文件上传接口
    
    上传文件到服务器工作空间
    """
    global file_handler
    
    if file_handler is None:
        raise HTTPException(status_code=503, detail="File handler not initialized")
    
    try:
        # 读取文件内容
        content = await file.read()
        
        # 保存文件
        result = file_handler.save_uploaded_file(file.filename, content)
        
        if result["success"]:
            return FileUploadResponse(
                success=True,
                filename=result["filename"],
                original_name=result["original_name"],
                filepath=result["filepath"],
                size=result["size"]
            )
        else:
            return FileUploadResponse(
                success=False,
                error=result.get("error", "上传失败")
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze-file", response_model=FileAnalyzeResponse)
async def analyze_file(request: FileAnalyzeRequest):
    """
    分析上传的文件
    
    读取文件内容并使用AI进行分析
    """
    global file_handler, langgraph_agent, chatbot
    
    if file_handler is None:
        raise HTTPException(status_code=503, detail="File handler not initialized")
    
    try:
        # 读取文件内容
        file_result = file_handler.read_uploaded_file_content(request.filepath)
        
        if not file_result["success"]:
            return FileAnalyzeResponse(
                success=False,
                error=file_result.get("error", "读取文件失败")
            )
        
        file_content = file_result["content"]
        file_type = file_result.get("file_type", "unknown")
        
        # 构建分析提示
        analysis_prompt = f"""用户上传了一个文件，请根据文件内容回答用户的问题。

文件类型: {file_type}
文件内容:
{file_content[:5000]}{"...(内容已截断)" if len(file_content) > 5000 else ""}

用户问题: {request.question}

请提供详细的分析和回答。"""
        
        # 使用AI分析
        if USE_LANGGRAPH and langgraph_agent:
            analysis = langgraph_agent.chat(analysis_prompt)
        elif chatbot:
            analysis = chatbot.chat(analysis_prompt)
        else:
            raise HTTPException(status_code=503, detail="No agent available")
        
        return FileAnalyzeResponse(
            success=True,
            analysis=analysis,
            file_type=file_type
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/files")
async def list_uploaded_files():
    """
    列出已上传的文件
    """
    global file_handler
    
    if file_handler is None:
        raise HTTPException(status_code=503, detail="File handler not initialized")
    
    try:
        result = file_handler.list_files("uploads")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    port = int(os.getenv("AGENT_PORT", "8000"))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
