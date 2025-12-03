"""
带有长时记忆的对话机器人 - LangChain 版本
使用 LangChain 框架实现对话链和记忆管理
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Optional
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import ConversationChain
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from memory_store import MemoryStore
import re

# 加载环境变量
load_dotenv()


class ChatbotWithMemory:
    """
    带有长时记忆功能的对话机器人（LangChain 版本）
    
    特性：
    1. 短时记忆：使用 LangChain ConversationBufferWindowMemory
    2. 长时记忆：使用向量数据库存储和检索
    3. 使用 LangChain LCEL 构建对话链
    4. 支持 DeepSeek API
    5. 从 JSON 文件加载多种 prompt 模板
    6. 支持文本总结、信息提取等多种功能
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: str = "deepseek-chat",
        memory_dir: str = "./memory_db",
        short_term_limit: int = 10,
        retrieve_memories: int = 5,
        prompts_file: str = "prompts.json"
    ):
        """
        初始化对话机器人
        
        Args:
            api_key: API密钥（DeepSeek）
            base_url: API基础URL
            model: 使用的模型名称
            memory_dir: 向量数据库存储目录
            short_term_limit: 短时记忆保留的对话轮数
            retrieve_memories: 每次检索的相关记忆数量
            prompts_file: prompt配置文件路径
        """
        # 获取配置
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        base_url = base_url or os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com")
        
        if not api_key:
            raise ValueError("请设置OPENAI_API_KEY环境变量或传入api_key参数（DeepSeek API Key）")
        
        # 加载 prompts 配置
        self.prompts = self._load_prompts(prompts_file)
        
        # 初始化 LangChain ChatOpenAI（兼容 DeepSeek）
        self.llm = ChatOpenAI(
            model=model,
            api_key=api_key,
            base_url=base_url,
            temperature=0.7,
            max_tokens=1000
        )
        
        self.model = model
        self.retrieve_memories = retrieve_memories
        
        # 初始化长时记忆存储（向量数据库）
        self.memory_store = MemoryStore(persist_directory=memory_dir)
        
        # 初始化短时记忆（LangChain 对话缓存）
        self.short_term_memory = ConversationBufferWindowMemory(
            k=short_term_limit,
            return_messages=True,
            memory_key="chat_history"
        )
        
        # 从配置文件获取系统提示词
        self.system_prompt = self.prompts.get("chat", {}).get("system_prompt", "你是一个有帮助的AI助手。")

        # 构建对话提示模板
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("system", "{memory_context}"),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ])
        
        # 构建 LCEL 链
        self.chain = self.prompt | self.llm | StrOutputParser()

    def _load_prompts(self, prompts_file: str) -> Dict:
        """
        从 JSON 文件加载 prompt 配置
        
        Args:
            prompts_file: prompt配置文件路径
            
        Returns:
            prompt配置字典
        """
        prompts_path = Path(prompts_file)
        
        # 如果是相对路径，从当前脚本目录查找
        if not prompts_path.is_absolute():
            script_dir = Path(__file__).parent
            prompts_path = script_dir / prompts_file
        
        try:
            with open(prompts_path, 'r', encoding='utf-8') as f:
                prompts = json.load(f)
            print(f"✓ 成功加载 prompt 配置文件: {prompts_path}")
            return prompts
        except FileNotFoundError:
            print(f"⚠ 未找到 prompt 配置文件: {prompts_path}，使用默认配置")
            return {
                "chat": {
                    "system_prompt": "你是一个友好、有帮助的AI助手。"
                }
            }
        except json.JSONDecodeError as e:
            print(f"⚠ prompt 配置文件格式错误: {e}，使用默认配置")
            return {
                "chat": {
                    "system_prompt": "你是一个友好、有帮助的AI助手。"
                }
            }

    def _build_memory_context(self, query: str) -> str:
        """
        基于用户查询构建记忆上下文
        """
        # 检索相关记忆
        relevant_memories = self.memory_store.search_memories(
            query, 
            n_results=self.retrieve_memories
        )
        
        if not relevant_memories:
            return "（暂无相关历史记忆）"
        
        # 构建记忆上下文
        memory_context = "【相关历史记忆】\n"
        for i, memory in enumerate(relevant_memories, 1):
            metadata = memory['metadata']
            timestamp = metadata.get('timestamp', '未知时间')[:10]
            
            if metadata.get('type') == 'fact':
                memory_context += f"{i}. [{timestamp}] 事实: {memory['content']}\n"
            else:
                memory_context += f"{i}. [{timestamp}] 对话:\n{memory['content']}\n"
        
        return memory_context
    
    def _extract_facts(self, user_message: str) -> List[str]:
        """
        从用户消息中提取重要事实信息
        """
        facts = []
        
        patterns = [
            (r'我(?:叫|是|名字是|的名字是)\s*([^\s,，。！!?？]+)', '用户的名字是{}'),
            (r'我(?:今年)?(\d+)\s*岁', '用户的年龄是{}岁'),
            (r'我(?:住在|在)\s*([^\s,，。！!?？]+)', '用户住在{}'),
            (r'我(?:喜欢|爱)\s*([^\s,，。！!?？]+)', '用户喜欢{}'),
            (r'我(?:不喜欢|讨厌)\s*([^\s,，。！!?？]+)', '用户不喜欢{}'),
            (r'我(?:是|做)\s*([\w]+)(?:工作|职业)?', '用户的职业是{}'),
            (r'我的(?:生日|出生日期)(?:是)?\s*(\d+月\d+日|\d+-\d+-\d+)', '用户的生日是{}'),
        ]
        
        for pattern, template in patterns:
            matches = re.findall(pattern, user_message)
            for match in matches:
                fact = template.format(match)
                facts.append(fact)
        
        return facts
    
    def chat(self, user_message: str) -> str:
        """
        处理用户消息并返回回复
        
        Args:
            user_message: 用户输入的消息
            
        Returns:
            助手的回复
        """
        # 获取相关的长时记忆
        memory_context = self._build_memory_context(user_message)
        
        # 获取短时记忆（对话历史）
        chat_history = self.short_term_memory.load_memory_variables({}).get("chat_history", [])
        
        # 调用 LangChain 链
        try:
            response = self.chain.invoke({
                "memory_context": memory_context,
                "chat_history": chat_history,
                "input": user_message
            })
        except Exception as e:
            response = f"抱歉，发生了错误: {str(e)}"
            return response
        
        # 更新短时记忆
        self.short_term_memory.save_context(
            {"input": user_message},
            {"output": response}
        )
        
        # 保存到长时记忆
        self.memory_store.add_memory(user_message, response)
        
        # 提取并保存事实信息
        facts = self._extract_facts(user_message)
        for fact in facts:
            self.memory_store.add_fact(fact, category="extracted")
        
        return response
    
    def summarize(self, text: str, max_length: Optional[int] = None) -> str:
        """
        对文本进行总结
        
        Args:
            text: 需要总结的文本
            max_length: 总结的最大长度（可选）
            
        Returns:
            总结后的文本
        """
        # 获取总结的 prompt 配置
        summarize_config = self.prompts.get("summarize", {})
        system_prompt = summarize_config.get("system_prompt", "你是一个专业的文本总结助手。")
        user_template = summarize_config.get("user_template", "请对以下文本进行总结：\n\n{text}")
        
        # 构建总结提示
        user_message = user_template.format(text=text)
        if max_length:
            user_message += f"\n\n要求：总结长度不超过{max_length}字。"
        
        # 创建简单的总结链
        summarize_prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", user_message)
        ])
        
        summarize_chain = summarize_prompt | self.llm | StrOutputParser()
        
        try:
            summary = summarize_chain.invoke({})
            return summary
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
        extract_config = self.prompts.get("extract_info", {})
        system_prompt = extract_config.get("system_prompt", "你是一个信息提取专家。")
        user_template = extract_config.get("user_template", "请从以下文本中提取关键信息：\n\n{text}")
        
        user_message = user_template.format(text=text)
        
        extract_prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", user_message)
        ])
        
        extract_chain = extract_prompt | self.llm | StrOutputParser()
        
        try:
            result = extract_chain.invoke({})
            return result
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
        translate_config = self.prompts.get("translate", {})
        system_prompt = translate_config.get("system_prompt", "你是一个专业的翻译助手。")
        user_template = translate_config.get("user_template", "请将以下文本翻译成{target_language}：\n\n{text}")
        
        user_message = user_template.format(text=text, target_language=target_language)
        
        translate_prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", user_message)
        ])
        
        translate_chain = translate_prompt | self.llm | StrOutputParser()
        
        try:
            result = translate_chain.invoke({})
            return result
        except Exception as e:
            return f"翻译失败: {str(e)}"
    
    def get_memory_stats(self) -> Dict:
        """获取记忆统计信息"""
        chat_history = self.short_term_memory.load_memory_variables({}).get("chat_history", [])
        return {
            "long_term_memories": self.memory_store.get_memory_count(),
            "short_term_messages": len(chat_history)
        }
    
    def clear_short_term_memory(self):
        """清空短时记忆"""
        self.short_term_memory.clear()
    
    def clear_all_memory(self):
        """清空所有记忆"""
        self.short_term_memory.clear()
        self.memory_store.clear_all_memories()
    
    def export_memories(self, filepath: str) -> bool:
        """导出长时记忆到文件"""
        return self.memory_store.export_memories(filepath)
    
    def get_retriever(self):
        """获取向量存储的 Retriever（用于 RAG）"""
        return self.memory_store.get_retriever()
