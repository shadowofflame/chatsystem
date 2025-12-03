"""
测试 LangGraph Agent 功能
"""

from langgraph_agent import LangGraphAgent
from dotenv import load_dotenv

load_dotenv()


def test_chat():
    """测试普通对话"""
    print("\n" + "="*60)
    print("测试 1: 普通对话")
    print("="*60)
    
    agent = LangGraphAgent()
    response = agent.chat("你好，请介绍一下你自己")
    print(f"\n回复: {response}\n")


def test_calculation():
    """测试计算功能"""
    print("\n" + "="*60)
    print("测试 2: 数学计算")
    print("="*60)
    
    agent = LangGraphAgent()
    response = agent.chat("帮我计算 125 * 48 + 360 / 12")
    print(f"\n回复: {response}\n")


def test_web_search():
    """测试网络搜索"""
    print("\n" + "="*60)
    print("测试 3: 网络搜索")
    print("="*60)
    
    agent = LangGraphAgent()
    response = agent.chat("2024年诺贝尔物理学奖获得者是谁?")
    print(f"\n回复: {response}\n")


def test_file_operations():
    """测试文件操作"""
    print("\n" + "="*60)
    print("测试 4: 文件操作")
    print("="*60)
    
    agent = LangGraphAgent()
    
    # 写文件
    response = agent.chat("帮我创建一个文件 test.txt，内容是'Hello, LangGraph!'")
    print(f"\n写文件回复: {response}\n")
    
    # 读文件
    response = agent.chat("读取 test.txt 文件的内容")
    print(f"\n读文件回复: {response}\n")
    
    # 列出文件
    response = agent.chat("列出当前目录的所有文件")
    print(f"\n列出文件回复: {response}\n")


def test_memory():
    """测试记忆功能"""
    print("\n" + "="*60)
    print("测试 5: 记忆功能")
    print("="*60)
    
    agent = LangGraphAgent()
    
    # 第一轮对话
    response = agent.chat("我叫张三，我喜欢编程")
    print(f"\n第一轮回复: {response}\n")
    
    # 第二轮对话 - 测试记忆
    response = agent.chat("你还记得我的名字和爱好吗？")
    print(f"\n第二轮回复: {response}\n")


def run_all_tests():
    """运行所有测试"""
    test_chat()
    test_calculation()
    # test_web_search()  # 需要网络连接
    test_file_operations()
    test_memory()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        test_name = sys.argv[1]
        if test_name == "chat":
            test_chat()
        elif test_name == "calc":
            test_calculation()
        elif test_name == "search":
            test_web_search()
        elif test_name == "file":
            test_file_operations()
        elif test_name == "memory":
            test_memory()
        else:
            print(f"未知测试: {test_name}")
            print("可用测试: chat, calc, search, file, memory")
    else:
        run_all_tests()
