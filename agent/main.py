"""
FastAPI Agent Server
提供 HTTP API 接口供 Java 后端调用
支持 --stdio 模式启用 LangGraph STDIO
支持流式输出 (SSE)
"""

import os
# 禁用 tokenizers 并行化警告
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import sys
import json
import asyncio
import argparse
import threading
from typing import Optional, List, AsyncGenerator
from contextlib import asynccontextmanager
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
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
    deep_think: bool = Field(default=False, description="是否启用深度思考(TOT)")
    thought_branches: int = Field(default=5, description="思考分支数量")
    thought_depth: int = Field(default=3, description="思考深度")


class ChatResponse(BaseModel):
    response: str = Field(..., description="助手回复")
    session_id: str = Field(..., description="会话ID")
    thinking_process: str = Field(default="", description="TOT思考过程")
    tot_score: float = Field(default=0.0, description="TOT最佳得分")
    deep_think: bool = Field(default=False, description="是否使用了深度思考")


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
    支持 deep_think 参数启用 TOT 深度思考，并返回思考过程
    """
    global chatbot, langgraph_agent
    
    if USE_LANGGRAPH:
        if langgraph_agent is None:
            raise HTTPException(status_code=503, detail="LangGraph Agent not initialized")
        
        try:
            # 如果启用联网搜索，使用带搜索的方法
            if request.enable_web_search:
                result = langgraph_agent.chat_with_search(
                    request.message,
                    deep_think=request.deep_think,
                    max_branches=request.thought_branches,
                    max_depth=request.thought_depth
                )
            else:
                result = langgraph_agent.chat(
                    request.message,
                    deep_think=request.deep_think,
                    max_branches=request.thought_branches,
                    max_depth=request.thought_depth
                )
            
            # result 现在是 dict，包含 response, thinking_process, tot_score, deep_think
            return ChatResponse(
                response=result.get("response", ""),
                session_id=request.session_id,
                thinking_process=result.get("thinking_process", ""),
                tot_score=result.get("tot_score", 0.0),
                deep_think=result.get("deep_think", False)
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
                session_id=request.session_id,
                thinking_process="",
                tot_score=0.0,
                deep_think=False
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


async def generate_sse_events(request: ChatRequest) -> AsyncGenerator[str, None]:
    """
    生成 SSE 事件流
    使用线程池执行同步生成器，避免阻塞事件循环
    """
    global langgraph_agent
    
    if langgraph_agent is None:
        yield f"data: {json.dumps({'type': 'error', 'content': 'Agent not initialized'})}\n\n"
        return
    
    try:
        # 选择流式方法
        if request.enable_web_search:
            stream_func = lambda: langgraph_agent.chat_with_search_stream(
                request.message,
                deep_think=request.deep_think,
                max_branches=request.thought_branches,
                max_depth=request.thought_depth
            )
        else:
            stream_func = lambda: langgraph_agent.chat_stream(
                request.message,
                deep_think=request.deep_think,
                max_branches=request.thought_branches,
                max_depth=request.thought_depth
            )
        
        # 使用队列来传递事件
        import queue
        event_queue = queue.Queue()
        stream_done = threading.Event()
        
        def run_stream():
            try:
                for event in stream_func():
                    event_queue.put(event)
                event_queue.put(None)  # 结束信号
            except Exception as e:
                event_queue.put({'type': 'error', 'content': str(e)})
                event_queue.put(None)
            finally:
                stream_done.set()
        
        # 在线程池中运行同步生成器
        loop = asyncio.get_event_loop()
        executor = ThreadPoolExecutor(max_workers=1)
        loop.run_in_executor(executor, run_stream)
        
        # 异步读取队列 - 使用更短的轮询间隔实现实时输出
        while True:
            try:
                # 使用阻塞式获取，超时10ms，实现近实时输出
                event = event_queue.get(timeout=0.01)
                if event is None:
                    yield f"data: {json.dumps({'type': 'done'})}\n\n"
                    return
                event_data = json.dumps(event, ensure_ascii=False)
                yield f"data: {event_data}\n\n"
            except queue.Empty:
                # 检查流是否已完成
                if stream_done.is_set() and event_queue.empty():
                    yield f"data: {json.dumps({'type': 'done'})}\n\n"
                    return
                await asyncio.sleep(0.005)  # 5ms 轮询，更流畅
        
    except Exception as e:
        error_event = json.dumps({'type': 'error', 'content': str(e)}, ensure_ascii=False)
        yield f"data: {error_event}\n\n"


@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    流式对话接口 (SSE)
    
    接收用户消息，以 Server-Sent Events 流式返回助手回复
    支持 enable_web_search 参数强制启用联网搜索
    支持 deep_think 参数启用 TOT 深度思考，边思考边输出
    """
    if not USE_LANGGRAPH:
        raise HTTPException(status_code=400, detail="Streaming only supported with LangGraph agent")
    
    return StreamingResponse(
        generate_sse_events(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # 禁用 nginx 缓冲
        }
    )


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


def run_stdio_mode(args):
    """运行 LangGraph STDIO 模式（纯命令行，不启动HTTP服务）"""
    print("🚀 启动 LangGraph STDIO 模式...")
    
    agent = LangGraphAgent(
        model=args.model,
        memory_dir=args.memory,
        workspace_dir=args.workspace,
        default_branches=args.branches,
        default_depth=args.depth,
    )
    
    sys.stdout.write("LangGraph STDIO ready. Type your message and press Enter.\n")
    sys.stdout.flush()
    
    for line in sys.stdin:
        message = line.strip()
        if not message:
            continue
        if message.lower() in ('exit', 'quit', 'q'):
            print("Goodbye!")
            break
        try:
            reply = agent.chat(
                message,
                deep_think=args.deep,
                max_branches=args.branches,
                max_depth=args.depth,
            )
        except Exception as exc:
            reply = f"error: {exc}"
        sys.stdout.write(reply + "\n")
        sys.stdout.flush()


def run_hybrid_mode(args):
    """
    混合模式：同时运行 HTTP API 服务和 STDIO 交互
    - HTTP API 在后台线程运行，供 Java 后端调用
    - STDIO 在主线程运行，可以直接命令行交互
    """
    import threading
    import time
    
    print("🚀 启动混合模式 (HTTP API + STDIO)...")
    print(f"   HTTP API: http://localhost:{args.port}")
    print(f"   深度思考: {'开启' if args.deep else '关闭'}")
    
    # 在后台线程启动 HTTP 服务
    def start_api():
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=args.port,
            reload=False,  # 混合模式下不能用 reload
            log_level="warning"  # 减少日志干扰
        )
    
    api_thread = threading.Thread(target=start_api, daemon=True)
    api_thread.start()
    
    # 等待 API 启动
    time.sleep(3)
    print(f"\n✅ HTTP API 已在后台运行 (端口 {args.port})")
    print("💬 STDIO 交互已就绪，输入消息后回车发送，输入 'quit' 退出\n")
    
    # 使用全局的 langgraph_agent（由 FastAPI lifespan 初始化）
    # 但这里需要单独创建一个，因为 lifespan 在另一个线程
    agent = LangGraphAgent(
        model=args.model,
        memory_dir=args.memory,
        workspace_dir=args.workspace,
        default_branches=args.branches,
        default_depth=args.depth,
    )
    
    # STDIO 交互循环
    try:
        while True:
            try:
                message = input("You: ").strip()
            except EOFError:
                break
            
            if not message:
                continue
            if message.lower() in ('exit', 'quit', 'q'):
                print("Goodbye!")
                break
            
            try:
                reply = agent.chat(
                    message,
                    deep_think=args.deep,
                    max_branches=args.branches,
                    max_depth=args.depth,
                )
                print(f"Agent: {reply}\n")
            except Exception as exc:
                print(f"Error: {exc}\n")
    except KeyboardInterrupt:
        print("\nGoodbye!")


def run_api_mode(port: int):
    """运行 FastAPI HTTP 模式"""
    print(f"🚀 启动 FastAPI HTTP 模式，端口: {port}")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Chatbot Agent - 支持 HTTP API、STDIO 和混合模式"
    )
    parser.add_argument(
        "--stdio", 
        action="store_true", 
        help="纯 STDIO 模式（不启动 HTTP 服务）"
    )
    parser.add_argument(
        "--hybrid", 
        action="store_true", 
        help="混合模式：同时运行 HTTP API 和 STDIO 交互"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=int(os.getenv("AGENT_PORT", "8000")), 
        help="HTTP API 端口 (默认: 8000)"
    )
    parser.add_argument(
        "--deep", 
        action="store_true", 
        help="启用深度思考 (Tree-of-Thought)"
    )
    parser.add_argument(
        "--branches", 
        type=int, 
        default=5, 
        help="思考分支数量 (默认: 5)"
    )
    parser.add_argument(
        "--depth", 
        type=int, 
        default=3, 
        help="思考深度 (默认: 3)"
    )
    parser.add_argument(
        "--model", 
        default="deepseek-chat", 
        help="模型名称 (默认: deepseek-chat)"
    )
    parser.add_argument(
        "--workspace", 
        default="./workspace", 
        help="工作区目录 (默认: ./workspace)"
    )
    parser.add_argument(
        "--memory", 
        default="./chat_memory_db", 
        help="记忆存储目录 (默认: ./chat_memory_db)"
    )
    
    args = parser.parse_args()
    
    if args.stdio:
        run_stdio_mode(args)
    elif args.hybrid:
        run_hybrid_mode(args)
    else:
        run_api_mode(args.port)
