"""
LangGraph Agent - 智能对话代理
使用 LangGraph 实现状态机架构，支持多种工具调用
"""

import json
from typing import TypedDict, Annotated, Sequence, Literal
from datetime import datetime

from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser

from tools import FileHandler, WebSearcher, Calculator
from memory_store import MemoryStore


class AgentState(TypedDict):
    """Agent状态定义"""
    messages: Annotated[Sequence[BaseMessage], "对话消息列表"]
    user_input: str  # 用户输入
    next_action: str  # 下一步动作: chat, search, file_operation, calculate, end
    tool_calls: list  # 工具调用列表
    tool_results: list  # 工具结果列表
    memory_context: str  # 记忆上下文
    final_response: str  # 最终响应
    needs_web_search: bool  # 是否需要网络搜索
    needs_file_operation: bool  # 是否需要文件操作
    needs_calculation: bool  # 是否需要计算


class LangGraphAgent:
    """
    基于 LangGraph 的智能对话代理
    
    工作流程:
    1. 接收用户输入
    2. 分析意图 (路由节点)
    3. 执行相应操作:
       - 网络搜索
       - 文件操作
       - 数学计算
       - 普通对话
    4. 整合结果并返回
    """
    
    def __init__(
        self,
        api_key: str = None,
        base_url: str = None,
        model: str = "deepseek-chat",
        memory_dir: str = "./memory_db",
        workspace_dir: str = "./workspace"
    ):
        """
        初始化 LangGraph Agent
        
        Args:
            api_key: API密钥
            base_url: API基础URL
            model: 模型名称
            memory_dir: 记忆存储目录
            workspace_dir: 工作空间目录
        """
        import os
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        base_url = base_url or os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com")
        
        # 初始化 LLM
        self.llm = ChatOpenAI(
            model=model,
            api_key=api_key,
            base_url=base_url,
            temperature=0.7,
            max_tokens=2000
        )
        
        # 初始化工具
        self.file_handler = FileHandler(workspace_dir)
        self.web_searcher = WebSearcher()
        self.calculator = Calculator()
        
        # 初始化记忆
        self.memory_store = MemoryStore(persist_directory=memory_dir)
        
        # 构建状态图
        self.graph = self._build_graph()
        self.app = self.graph.compile()
    
    def _build_graph(self) -> StateGraph:
        """构建 LangGraph 状态图"""
        
        workflow = StateGraph(AgentState)
        
        # 添加节点
        workflow.add_node("analyze_intent", self._analyze_intent)  # 意图分析
        workflow.add_node("retrieve_memory", self._retrieve_memory)  # 检索记忆
        workflow.add_node("web_search", self._web_search)  # 网络搜索
        workflow.add_node("file_operation", self._file_operation)  # 文件操作
        workflow.add_node("calculate", self._calculate)  # 计算
        workflow.add_node("generate_response", self._generate_response)  # 生成响应
        workflow.add_node("save_memory", self._save_memory)  # 保存记忆
        
        # 设置入口
        workflow.set_entry_point("analyze_intent")
        
        # 添加条件边：根据意图路由
        workflow.add_conditional_edges(
            "analyze_intent",
            self._route_decision,
            {
                "memory": "retrieve_memory",
                "search": "web_search",
                "file": "file_operation",
                "calculate": "calculate",
                "chat": "retrieve_memory"
            }
        )
        
        # 从记忆检索到响应生成
        workflow.add_edge("retrieve_memory", "generate_response")
        
        # 从工具节点到响应生成
        workflow.add_edge("web_search", "generate_response")
        workflow.add_edge("file_operation", "generate_response")
        workflow.add_edge("calculate", "generate_response")
        
        # 从响应生成到保存记忆
        workflow.add_edge("generate_response", "save_memory")
        
        # 从保存记忆到结束
        workflow.add_edge("save_memory", END)
        
        return workflow
    
    def _analyze_intent(self, state: AgentState) -> AgentState:
        """
        分析用户意图
        
        判断用户需要:
        - 网络搜索 (最新信息、新闻、实时数据)
        - 文件操作 (读写文件、查看目录)
        - 计算 (数学计算、数据处理)
        - 普通对话
        """
        user_input = state["user_input"]
        
        # 使用 LLM 分析意图
        intent_prompt = f"""分析用户的意图，判断需要执行什么操作。

用户输入: {user_input}

请判断用户的意图并返回JSON格式:
{{
    "intent": "search|file|calculate|chat",
    "reason": "判断理由",
    "needs_web_search": true/false,
    "needs_file_operation": true/false,
    "needs_calculation": true/false
}}

判断标准:
- search: 需要最新信息、新闻、实时数据、天气等
- file: 涉及读写文件、查看目录、保存内容等
- calculate: 需要数学计算、数据处理
- chat: 普通对话、回答知识性问题

只返回JSON，不要其他内容。"""
        
        try:
            response = self.llm.invoke([HumanMessage(content=intent_prompt)])
            intent_data = json.loads(response.content)
            
            state["next_action"] = intent_data.get("intent", "chat")
            state["needs_web_search"] = intent_data.get("needs_web_search", False)
            state["needs_file_operation"] = intent_data.get("needs_file_operation", False)
            state["needs_calculation"] = intent_data.get("needs_calculation", False)
            
            print(f"🔍 意图分析: {intent_data.get('intent')} - {intent_data.get('reason')}")
            
        except Exception as e:
            print(f"⚠️ 意图分析失败，默认为普通对话: {e}")
            state["next_action"] = "chat"
            state["needs_web_search"] = False
            state["needs_file_operation"] = False
            state["needs_calculation"] = False
        
        return state
    
    def _route_decision(self, state: AgentState) -> Literal["memory", "search", "file", "calculate", "chat"]:
        """路由决策"""
        if state.get("needs_web_search"):
            return "search"
        elif state.get("needs_file_operation"):
            return "file"
        elif state.get("needs_calculation"):
            return "calculate"
        else:
            return "memory"
    
    def _retrieve_memory(self, state: AgentState) -> AgentState:
        """检索相关记忆"""
        user_input = state["user_input"]
        
        # 检索相关记忆
        relevant_memories = self.memory_store.search_memories(user_input, n_results=5)
        
        if relevant_memories:
            memory_context = "【相关历史记忆】\n"
            for i, memory in enumerate(relevant_memories, 1):
                memory_context += f"{i}. {memory['content']}\n"
        else:
            memory_context = "（暂无相关历史记忆）"
        
        state["memory_context"] = memory_context
        print(f"📚 检索到 {len(relevant_memories)} 条相关记忆")
        
        return state
    
    def _web_search(self, state: AgentState) -> AgentState:
        """执行网络搜索"""
        user_input = state["user_input"]
        
        print(f"🌐 执行网络搜索: {user_input}")
        search_result = self.web_searcher.search(user_input, num_results=5)
        
        if search_result["success"]:
            results_text = "【网络搜索结果】\n"
            for i, result in enumerate(search_result["results"], 1):
                results_text += f"{i}. {result['title']}\n"
                results_text += f"   {result['snippet']}\n"
                results_text += f"   来源: {result['link']}\n\n"
            
            state["tool_results"] = [{"type": "search", "content": results_text}]
            state["memory_context"] = results_text
        else:
            state["tool_results"] = [{"type": "search", "content": f"搜索失败: {search_result.get('error')}"}]
            state["memory_context"] = "搜索未能返回结果"
        
        return state
    
    def _file_operation(self, state: AgentState) -> AgentState:
        """执行文件操作"""
        user_input = state["user_input"]
        
        print(f"📁 执行文件操作")
        
        # 使用LLM解析文件操作意图
        file_prompt = f"""用户想要执行文件操作，请解析具体操作并返回JSON格式:

用户输入: {user_input}

返回格式:
{{
    "operation": "read|write|list|delete",
    "filepath": "文件路径",
    "content": "写入内容（仅write操作需要）"
}}

只返回JSON，不要其他内容。"""
        
        try:
            response = self.llm.invoke([HumanMessage(content=file_prompt)])
            file_op = json.loads(response.content)
            
            operation = file_op.get("operation")
            filepath = file_op.get("filepath", "")
            
            if operation == "read":
                result = self.file_handler.read_file(filepath)
            elif operation == "write":
                content = file_op.get("content", "")
                result = self.file_handler.write_file(filepath, content)
            elif operation == "list":
                result = self.file_handler.list_files(filepath or ".")
            elif operation == "delete":
                result = self.file_handler.delete_file(filepath)
            else:
                result = {"success": False, "error": "未知的文件操作"}
            
            state["tool_results"] = [{"type": "file", "content": json.dumps(result, ensure_ascii=False, indent=2)}]
            state["memory_context"] = f"文件操作结果: {json.dumps(result, ensure_ascii=False)}"
            
        except Exception as e:
            error_msg = f"文件操作解析失败: {str(e)}"
            state["tool_results"] = [{"type": "file", "content": error_msg}]
            state["memory_context"] = error_msg
        
        return state
    
    def _calculate(self, state: AgentState) -> AgentState:
        """执行计算"""
        user_input = state["user_input"]
        
        print(f"🧮 执行计算")
        
        # 使用LLM提取数学表达式
        calc_prompt = f"""从用户输入中提取数学表达式并返回JSON:

用户输入: {user_input}

返回格式:
{{
    "expression": "数学表达式（如: 2 + 2, 3 * 5 + 10）"
}}

只返回JSON，不要其他内容。"""
        
        try:
            response = self.llm.invoke([HumanMessage(content=calc_prompt)])
            calc_op = json.loads(response.content)
            
            expression = calc_op.get("expression", "")
            result = self.calculator.calculate(expression)
            
            state["tool_results"] = [{"type": "calculate", "content": json.dumps(result, ensure_ascii=False)}]
            state["memory_context"] = f"计算结果: {result}"
            
        except Exception as e:
            error_msg = f"计算失败: {str(e)}"
            state["tool_results"] = [{"type": "calculate", "content": error_msg}]
            state["memory_context"] = error_msg
        
        return state
    
    def _generate_response(self, state: AgentState) -> AgentState:
        """生成最终响应"""
        user_input = state["user_input"]
        memory_context = state.get("memory_context", "")
        tool_results = state.get("tool_results", [])
        
        # 构建上下文
        context_parts = []
        
        if memory_context:
            context_parts.append(memory_context)
        
        if tool_results:
            for result in tool_results:
                context_parts.append(f"\n【{result['type']}工具结果】\n{result['content']}")
        
        full_context = "\n".join(context_parts)
        
        # 生成响应
        response_prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个智能助手。根据提供的上下文信息回答用户问题。

要求:
1. 如果有搜索结果，基于搜索结果回答
2. 如果有文件操作结果，说明操作结果
3. 如果有计算结果，给出计算答案
4. 回答要准确、友好、有帮助
5. 如果信息不足，诚实说明

上下文信息:
{context}"""),
            ("human", "{input}")
        ])
        
        chain = response_prompt | self.llm | StrOutputParser()
        
        try:
            response = chain.invoke({
                "context": full_context,
                "input": user_input
            })
            
            state["final_response"] = response
            print(f"✅ 生成响应完成")
            
        except Exception as e:
            state["final_response"] = f"抱歉，生成响应时出错: {str(e)}"
        
        return state
    
    def _save_memory(self, state: AgentState) -> AgentState:
        """保存对话到记忆"""
        user_input = state["user_input"]
        final_response = state.get("final_response", "")
        
        # 保存到长期记忆
        self.memory_store.add_memory(user_input, final_response)
        print(f"💾 保存记忆完成")
        
        return state
    
    def chat(self, user_input: str) -> str:
        """
        处理用户输入
        
        Args:
            user_input: 用户输入
            
        Returns:
            AI响应
        """
        # 初始化状态
        initial_state = {
            "messages": [],
            "user_input": user_input,
            "next_action": "",
            "tool_calls": [],
            "tool_results": [],
            "memory_context": "",
            "final_response": "",
            "needs_web_search": False,
            "needs_file_operation": False,
            "needs_calculation": False
        }
        
        # 运行状态图
        print(f"\n{'='*50}")
        print(f"📝 用户输入: {user_input}")
        print(f"{'='*50}\n")
        
        final_state = self.app.invoke(initial_state)
        
        return final_state["final_response"]
    
    def chat_with_search(self, user_input: str) -> str:
        """
        强制使用联网搜索处理用户输入
        
        Args:
            user_input: 用户输入
            
        Returns:
            AI响应
        """
        print(f"\n{'='*50}")
        print(f"📝 用户输入: {user_input}")
        print(f"🌐 强制联网搜索模式")
        print(f"{'='*50}\n")
        
        # 执行网络搜索
        print(f"🔍 执行网络搜索: {user_input}")
        search_result = self.web_searcher.search(user_input, num_results=5)
        
        if search_result["success"]:
            results_text = "【网络搜索结果】\n"
            for i, result in enumerate(search_result["results"], 1):
                results_text += f"{i}. {result['title']}\n"
                results_text += f"   {result['snippet']}\n"
                results_text += f"   来源: {result['link']}\n\n"
            print(f"✅ 搜索成功，获取 {len(search_result['results'])} 条结果")
        else:
            results_text = f"搜索未能返回结果: {search_result.get('error', '未知错误')}"
            print(f"⚠️ 搜索失败: {search_result.get('error')}")
        
        # 检索相关记忆
        relevant_memories = self.memory_store.search_memories(user_input, n_results=3)
        memory_context = ""
        if relevant_memories:
            memory_context = "\n\n【相关历史记忆】\n"
            for i, memory in enumerate(relevant_memories, 1):
                memory_context += f"{i}. {memory['content']}\n"
        
        # 生成响应
        response_prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个智能助手，能够利用网络搜索结果回答用户问题。

要求:
1. 基于搜索结果回答问题
2. 如有多个来源，综合信息回答
3. 适当引用来源
4. 如果搜索结果不足以回答问题，诚实说明
5. 回答要准确、有帮助

{context}"""),
            ("human", "{input}")
        ])
        
        chain = response_prompt | self.llm | StrOutputParser()
        
        try:
            response = chain.invoke({
                "context": results_text + memory_context,
                "input": user_input
            })
            print(f"✅ 生成响应完成")
            
            # 保存到长期记忆
            self.memory_store.add_memory(user_input, response)
            print(f"💾 保存记忆完成")
            
            return response
            
        except Exception as e:
            error_msg = f"抱歉，生成响应时出错: {str(e)}"
            print(f"❌ 错误: {error_msg}")
            return error_msg
    
    def get_memory_stats(self):
        """获取记忆统计"""
        return {
            "long_term_memories": self.memory_store.get_memory_count()
        }
    
    def clear_all_memory(self):
        """清除所有记忆"""
        self.memory_store.clear_all_memories()
    
    def summarize(self, text: str, max_length: int = None) -> str:
        """
        对文本进行总结
        
        Args:
            text: 需要总结的文本
            max_length: 总结的最大长度（可选）
            
        Returns:
            总结后的文本
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一个专业的文本总结助手。请简洁、准确地总结用户提供的文本。"),
            ("human", f"请对以下文本进行总结：\n\n{text}" + (f"\n\n要求：总结长度不超过{max_length}字。" if max_length else ""))
        ])
        
        chain = prompt | self.llm | StrOutputParser()
        
        try:
            return chain.invoke({})
        except Exception as e:
            return f"总结失败: {str(e)}"
    
    def extract_information(self, text: str) -> str:
        """
        从文本中提取关键信息
        
        Args:
            text: 需要提取信息的文本
            
        Returns:
            提取的关键信息
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一个信息提取专家。请从用户提供的文本中提取关键信息，包括人物、时间、地点、事件等重要内容。"),
            ("human", f"请从以下文本中提取关键信息：\n\n{text}")
        ])
        
        chain = prompt | self.llm | StrOutputParser()
        
        try:
            return chain.invoke({})
        except Exception as e:
            return f"信息提取失败: {str(e)}"
    
    def translate(self, text: str, target_language: str = "English") -> str:
        """
        翻译文本
        
        Args:
            text: 需要翻译的文本
            target_language: 目标语言
            
        Returns:
            翻译后的文本
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"你是一个专业的翻译助手。请将用户提供的文本准确翻译成{target_language}。只返回翻译结果，不要添加解释。"),
            ("human", text)
        ])
        
        chain = prompt | self.llm | StrOutputParser()
        
        try:
            return chain.invoke({})
        except Exception as e:
            return f"翻译失败: {str(e)}"
