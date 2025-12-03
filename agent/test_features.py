"""
测试 ChatbotWithMemory 的新功能
包括：从JSON加载prompt、文本总结、信息提取、翻译等
"""

from chatbot import ChatbotWithMemory


def test_chat():
    """测试基本对话功能"""
    print("=" * 60)
    print("测试 1: 基本对话功能")
    print("=" * 60)
    
    bot = ChatbotWithMemory()
    
    # 对话测试
    response = bot.chat("你好，我叫小明，今年25岁，住在北京。")
    print(f"用户: 你好，我叫小明，今年25岁，住在北京。")
    print(f"助手: {response}\n")
    
    response = bot.chat("你记得我的名字吗？")
    print(f"用户: 你记得我的名字吗？")
    print(f"助手: {response}\n")


def test_summarize():
    """测试文本总结功能"""
    print("=" * 60)
    print("测试 2: 文本总结功能")
    print("=" * 60)
    
    bot = ChatbotWithMemory()
    
    long_text = """
    人工智能（Artificial Intelligence，简称AI）是计算机科学的一个分支，
    它企图了解智能的实质，并生产出一种新的能以人类智能相似的方式做出反应的智能机器。
    该领域的研究包括机器人、语言识别、图像识别、自然语言处理和专家系统等。
    
    人工智能从诞生以来，理论和技术日益成熟，应用领域也不断扩大。可以设想，
    未来人工智能带来的科技产品，将会是人类智慧的"容器"。人工智能可以对人的意识、
    思维的信息过程进行模拟。人工智能不是人的智能，但能像人那样思考、也可能超过人的智能。
    
    人工智能的应用领域非常广泛，包括医疗诊断、股票交易、机器人控制、法律咨询、
    遥控操作和科学发现等。在医疗领域，AI可以协助医生进行疾病诊断和治疗方案制定。
    在金融领域，AI被用于风险评估和投资决策。在交通领域，自动驾驶技术正在改变
    人们的出行方式。
    """
    
    print(f"原文本长度: {len(long_text)} 字\n")
    print("原文本:")
    print(long_text)
    print("\n" + "-" * 60)
    
    summary = bot.summarize(long_text, max_length=200)
    print("\n总结结果:")
    print(summary)
    print()


def test_extract_information():
    """测试信息提取功能"""
    print("=" * 60)
    print("测试 3: 信息提取功能")
    print("=" * 60)
    
    bot = ChatbotWithMemory()
    
    text = """
    2024年3月15日，OpenAI公司在美国旧金山举行新闻发布会，
    CEO Sam Altman宣布推出最新的GPT-4模型。该模型在多项基准测试中
    表现出色，准确率达到了95%以上。新模型将于4月1日正式对外开放API接口，
    价格为每1000个token 0.03美元。
    """
    
    print("原文本:")
    print(text)
    print("\n" + "-" * 60)
    
    extracted = bot.extract_information(text)
    print("\n提取的关键信息:")
    print(extracted)
    print()


def test_translate():
    """测试翻译功能"""
    print("=" * 60)
    print("测试 4: 翻译功能")
    print("=" * 60)
    
    bot = ChatbotWithMemory()
    
    chinese_text = "人工智能正在改变我们的生活方式，从智能手机到自动驾驶汽车，AI技术无处不在。"
    
    print(f"中文原文: {chinese_text}")
    print("\n" + "-" * 60)
    
    english = bot.translate(chinese_text, "English")
    print(f"\n英文翻译:\n{english}")
    print()


def test_memory_stats():
    """测试记忆统计功能"""
    print("=" * 60)
    print("测试 5: 记忆统计")
    print("=" * 60)
    
    bot = ChatbotWithMemory()
    
    # 进行几轮对话
    bot.chat("我喜欢打篮球")
    bot.chat("我的生日是5月20日")
    bot.chat("我在一家科技公司工作")
    
    stats = bot.get_memory_stats()
    print(f"长时记忆数量: {stats['long_term_memories']}")
    print(f"短时记忆消息数: {stats['short_term_messages']}")
    print()


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("ChatbotWithMemory 新功能测试")
    print("=" * 60 + "\n")
    
    try:
        # test_chat()
        test_summarize()
        # test_extract_information()
        # test_translate()
        # test_memory_stats()
        
        print("=" * 60)
        print("所有测试完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
