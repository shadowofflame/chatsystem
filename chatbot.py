"""
带有长时记忆的对话机器人 - LangChain 版本
使用 LangChain 框架实现对话链和记忆管理
"""

import os
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
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: str = "deepseek-chat",
        memory_dir: str = "./memory_db",
        short_term_limit: int = 10,
        retrieve_memories: int = 5
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
        """
        # 获取配置
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        base_url = base_url or os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com")
        
        if not api_key:
            raise ValueError("请设置OPENAI_API_KEY环境变量或传入api_key参数（DeepSeek API Key）")
        
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
        
        # 系统提示词
        self.system_prompt = """你是一个友好、有帮助的AI助手，具有长时记忆能力。

你的特点：
1. 你能记住与用户之前的对话内容
2. 你会主动关联之前的对话信息来提供更个性化的回复
3. 你会注意用户提到的个人信息、偏好和重要事项
4. 当用户询问之前讨论过的内容时，你会尽力回忆并提供准确的信息

在回复时：
- 如果检索到相关的历史记忆，自然地将其融入对话中
- 不要生硬地说"根据我的记忆"，而是自然地引用之前的对话
- 如果用户提供了新的个人信息，在对话中确认并记住它
- 保持友好和个性化的对话风格"""

        # 构建对话提示模板
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("system", "{memory_context}"),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ])
        
        # 构建 LCEL 链
        self.chain = self.prompt | self.llm | StrOutputParser()

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


def main():
    """交互式对话主函数"""
    print("=" * 60)
    print("   带有长时记忆的对话机器人 (LangChain + DeepSeek)")
    print("   - 输入 'quit' 或 'exit' 退出")
    print("   - 输入 'clear' 清空当前会话记忆")
    print("   - 输入 'stats' 查看记忆统计")
    print("   - 输入 'forget' 清空所有记忆")
    print("=" * 60)
    
    try:
        chatbot = ChatbotWithMemory(
            memory_dir="./chat_memory_db",
            short_term_limit=10,
            retrieve_memories=5
        )
    except ValueError as e:
        print(f"\n错误: {e}")
        print("请创建 .env 文件并设置 OPENAI_API_KEY")
        return
    
    stats = chatbot.get_memory_stats()
    print(f"\n已加载 {stats['long_term_memories']} 条长时记忆\n")
    
    while True:
        try:
            user_input = input("你: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见！")
            break
        
        if not user_input:
            continue
        
        if user_input.lower() in ['quit', 'exit']:
            print("再见！期待下次与你对话！")
            break
        
        if user_input.lower() == 'clear':
            chatbot.clear_short_term_memory()
            print("[已清空当前会话记忆，长时记忆保留]\n")
            continue
        
        if user_input.lower() == 'stats':
            stats = chatbot.get_memory_stats()
            print(f"[记忆统计]")
            print(f"  长时记忆: {stats['long_term_memories']} 条")
            print(f"  短时记忆: {stats['short_term_messages']} 条消息\n")
            continue
        
        if user_input.lower() == 'forget':
            confirm = input("确定要清空所有记忆吗？(yes/no): ")
            if confirm.lower() == 'yes':
                chatbot.clear_all_memory()
                print("[已清空所有记忆]\n")
            else:
                print("[已取消]\n")
            continue
        
        # 正常对话
        response = chatbot.chat(user_input)
        print(f"\n助手: {response}\n")


if __name__ == "__main__":
    main()
