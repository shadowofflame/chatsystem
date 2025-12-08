"""
LangGraph Studio 入口文件
用于在 LangGraph Studio 网页界面中运行 Agent
"""

from langgraph_agent import LangGraphAgent

# 创建 Agent 实例
_agent = LangGraphAgent(
    memory_dir="./chat_memory_db",
    workspace_dir="./workspace"
)

# 导出 graph 供 LangGraph Studio 使用
graph = _agent.graph
