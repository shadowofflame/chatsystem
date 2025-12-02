"""
长时记忆存储模块 - LangChain 版本
使用 LangChain + ChromaDB 实现向量存储和检索
"""

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document
from datetime import datetime
from typing import List, Dict, Optional
import json
import os


class MemoryStore:
    """
    基于 LangChain + ChromaDB 的长时记忆存储
    
    特性：
    1. 使用 LangChain 封装的 HuggingFace Embeddings
    2. 使用 LangChain 封装的 ChromaDB
    3. 支持按相似度检索相关记忆
    4. 支持记忆的时间戳和元数据
    """
    
    def __init__(
        self,
        persist_directory: str = "./chroma_db",
        collection_name: str = "chat_memory",
        embedding_model: str = "paraphrase-multilingual-MiniLM-L12-v2"
    ):
        """
        初始化记忆存储
        
        Args:
            persist_directory: ChromaDB持久化目录
            collection_name: 集合名称
            embedding_model: HuggingFace 嵌入模型名称
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        
        # 初始化嵌入模型（使用 LangChain 封装）
        print(f"正在加载嵌入模型: {embedding_model}")
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # 初始化或加载 ChromaDB 向量存储
        self.vectorstore = Chroma(
            collection_name=collection_name,
            embedding_function=self.embeddings,
            persist_directory=persist_directory
        )
        
        print(f"记忆存储初始化完成，当前记忆数量: {self.get_memory_count()}")
    
    def add_memory(
        self,
        user_message: str,
        assistant_response: str,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        添加一条对话记忆
        
        Args:
            user_message: 用户消息
            assistant_response: 助手回复
            metadata: 额外的元数据
            
        Returns:
            记忆ID
        """
        timestamp = datetime.now().isoformat()
        
        # 组合对话内容
        combined_content = f"用户: {user_message}\n助手: {assistant_response}"
        
        # 准备元数据
        memory_metadata = {
            "user_message": user_message,
            "assistant_response": assistant_response,
            "timestamp": timestamp,
            "type": "conversation"
        }
        
        if metadata:
            memory_metadata.update(metadata)
        
        # 创建 LangChain Document
        doc = Document(
            page_content=combined_content,
            metadata=memory_metadata
        )
        
        # 添加到向量存储
        ids = self.vectorstore.add_documents([doc])
        
        return ids[0] if ids else ""
    
    def add_fact(self, fact: str, category: str = "general") -> str:
        """
        添加一条事实记忆
        
        Args:
            fact: 事实内容
            category: 分类
            
        Returns:
            记忆ID
        """
        timestamp = datetime.now().isoformat()
        
        metadata = {
            "fact": fact,
            "category": category,
            "timestamp": timestamp,
            "type": "fact"
        }
        
        doc = Document(
            page_content=fact,
            metadata=metadata
        )
        
        ids = self.vectorstore.add_documents([doc])
        
        return ids[0] if ids else ""
    
    def search_memories(
        self,
        query: str,
        n_results: int = 5,
        memory_type: Optional[str] = None
    ) -> List[Dict]:
        """
        根据查询搜索相关记忆
        
        Args:
            query: 查询文本
            n_results: 返回结果数量
            memory_type: 过滤记忆类型（conversation/fact）
            
        Returns:
            相关记忆列表
        """
        if self.get_memory_count() == 0:
            return []
        
        # 构建过滤条件
        filter_dict = None
        if memory_type:
            filter_dict = {"type": memory_type}
        
        # 使用 LangChain 的相似度搜索
        results = self.vectorstore.similarity_search_with_score(
            query,
            k=n_results,
            filter=filter_dict
        )
        
        # 格式化结果
        memories = []
        for doc, score in results:
            memory = {
                "id": doc.metadata.get("id", ""),
                "content": doc.page_content,
                "metadata": doc.metadata,
                "distance": score
            }
            memories.append(memory)
        
        return memories
    
    def get_retriever(self, search_kwargs: Optional[Dict] = None):
        """
        获取 LangChain Retriever 对象
        
        Args:
            search_kwargs: 搜索参数
            
        Returns:
            VectorStoreRetriever
        """
        if search_kwargs is None:
            search_kwargs = {"k": 5}
        
        return self.vectorstore.as_retriever(search_kwargs=search_kwargs)
    
    def get_recent_memories(self, n: int = 10) -> List[Dict]:
        """
        获取最近的记忆（按时间排序）
        """
        # 获取所有文档
        all_docs = self.vectorstore.get()
        
        if not all_docs or not all_docs.get('documents'):
            return []
        
        # 组合并按时间排序
        memories = []
        documents = all_docs.get('documents', [])
        metadatas = all_docs.get('metadatas', [])
        ids = all_docs.get('ids', [])
        
        for i, doc_content in enumerate(documents):
            memories.append({
                "id": ids[i] if i < len(ids) else "",
                "content": doc_content,
                "metadata": metadatas[i] if i < len(metadatas) else {}
            })
        
        # 按时间戳排序
        memories.sort(
            key=lambda x: x['metadata'].get('timestamp', ''),
            reverse=True
        )
        
        return memories[:n]
    
    def delete_memory(self, memory_id: str) -> bool:
        """删除指定记忆"""
        try:
            self.vectorstore.delete([memory_id])
            return True
        except Exception as e:
            print(f"删除记忆失败: {e}")
            return False
    
    def clear_all_memories(self) -> bool:
        """清空所有记忆"""
        try:
            # 获取所有ID并删除
            all_data = self.vectorstore.get()
            if all_data and all_data.get('ids'):
                self.vectorstore.delete(all_data['ids'])
            return True
        except Exception as e:
            print(f"清空记忆失败: {e}")
            return False
    
    def get_memory_count(self) -> int:
        """获取记忆数量"""
        try:
            all_data = self.vectorstore.get()
            return len(all_data.get('ids', [])) if all_data else 0
        except:
            return 0
    
    def export_memories(self, filepath: str) -> bool:
        """导出所有记忆到JSON文件"""
        try:
            all_data = self.vectorstore.get()
            
            if not all_data:
                return False
            
            export_data = []
            documents = all_data.get('documents', [])
            metadatas = all_data.get('metadatas', [])
            ids = all_data.get('ids', [])
            
            for i, doc_content in enumerate(documents):
                export_data.append({
                    "id": ids[i] if i < len(ids) else "",
                    "content": doc_content,
                    "metadata": metadatas[i] if i < len(metadatas) else {}
                })
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"导出记忆失败: {e}")
            return False


# 测试代码
if __name__ == "__main__":
    # 初始化记忆存储
    memory = MemoryStore(persist_directory="./test_chroma_db")
    
    # 添加测试记忆
    memory.add_memory(
        "我叫张三，今年25岁",
        "你好张三！很高兴认识你。"
    )
    
    memory.add_memory(
        "我喜欢编程和打篮球",
        "编程和篮球都是很棒的爱好！"
    )
    
    memory.add_fact("用户名字是张三", category="personal_info")
    memory.add_fact("用户喜欢编程", category="preference")
    
    # 测试搜索
    print("\n搜索'名字'相关记忆:")
    results = memory.search_memories("我的名字是什么", n_results=3)
    for r in results:
        print(f"  - {r['content'][:50]}... (距离: {r['distance']:.4f})")
    
    print(f"\n总记忆数量: {memory.get_memory_count()}")
