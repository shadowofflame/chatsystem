"""
FastAPI Agent Server
提供 HTTP API 接口供 Java 后端调用
"""

import os
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

from chatbot import ChatbotWithMemory


# 全局 chatbot 实例
chatbot: Optional[ChatbotWithMemory] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global chatbot
    print("正在初始化 Chatbot Agent...")
    try:
        chatbot = ChatbotWithMemory(
            memory_dir="./chat_memory_db",
            short_term_limit=10,
            retrieve_memories=5
        )
        print("Chatbot Agent 初始化完成")
    except Exception as e:
        print(f"初始化失败: {e}")
        raise
    
    yield
    
    print("正在关闭 Chatbot Agent...")


# 创建 FastAPI 应用
app = FastAPI(
    title="Chatbot Agent API",
    description="带有长时记忆的对话机器人 Agent 服务",
    version="1.0.0",
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
    """
    global chatbot
    
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
    global chatbot
    
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
    global chatbot
    
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
    global chatbot
    
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
    global chatbot
    
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
    global chatbot
    
    if chatbot is None:
        raise HTTPException(status_code=503, detail="Chatbot not initialized")
    
    try:
        translated = chatbot.translate(request.text, request.target_language)
        return TranslateResponse(translated_text=translated)
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
