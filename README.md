# 智能对话助手 - 全栈版

基于 **Java 21 + Spring Boot 3 + Python Agent + Vue 3** 的智能对话机器人，具有长时记忆和**深度思考 (Tree-of-Thoughts)** 功能。

## ✨ 新增功能

- 🧠 **深度思考 (TOT)** - Tree-of-Thoughts 多分支推理
- 🎨 **LangGraph Studio** - 可视化调试界面
- 💬 **STDIO 模式** - 命令行交互支持
- 🔄 **混合模式** - HTTP API + STDIO 同时运行

## 📁 项目结构

```
chatbot-with-memory/
├── backend/                 # Java 后端 (Spring Boot 3 + Java 21)
│   ├── src/
│   │   └── main/
│   │       ├── java/com/chatbot/
│   │       │   ├── ChatbotApplication.java
│   │       │   ├── config/
│   │       │   ├── controller/
│   │       │   ├── dto/
│   │       │   └── service/
│   │       └── resources/
│   │           └── application.yml
│   └── pom.xml
├── agent/                   # Python Agent (FastAPI + LangGraph)
│   ├── main.py              # 多模式入口 (API/STDIO/混合)
│   ├── langgraph_agent.py   # LangGraph 状态机 Agent
│   ├── langgraph_studio.py  # LangGraph Studio 入口
│   ├── tot_reasoner.py      # Tree-of-Thoughts 深度思考
│   ├── memory_store.py      # 向量记忆存储
│   ├── tools.py             # 工具集 (搜索/文件/计算)
│   ├── langgraph.json       # LangGraph Studio 配置
│   └── requirements.txt
├── frontend/                # 前端 (Vue 3 + Vite)
│   ├── src/
│   │   ├── App.vue          # 主界面 (含深度思考开关)
│   │   ├── main.js
│   │   ├── style.css
│   │   └── api/
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## 🏗️ 系统架构

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│    Frontend     │────▶│  Java Backend   │────▶│  Python Agent   │
│   (Vue 3)       │     │ (Spring Boot)   │     │   (LangGraph)   │
│   Port: 5173    │     │   Port: 9090    │     │   Port: 8000    │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                         │
                              ┌──────────────────────────┼──────────────────────────┐
                              │                          │                          │
                              ▼                          ▼                          ▼
                    ┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
                    │   ChromaDB      │      │  TOT Reasoner   │      │  LangGraph      │
                    │  (向量记忆)      │      │  (深度思考)      │      │  Studio (2024)  │
                    └─────────────────┘      └─────────────────┘      └─────────────────┘
```

## 🚀 快速开始

### 环境要求

- **Java**: 21+
- **Maven**: 3.8+
- **Python**: 3.11+ (推荐 3.11-3.12，3.13 需要特定版本)
- **Node.js**: 18+
- **npm**: 9+
- **MySQL**: 8.0+

### 1. 启动 Python Agent

```bash
cd agent

# 创建虚拟环境
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
copy .env.example .env
# 编辑 .env 文件，设置你的 DeepSeek API Key

# 启动服务 (多种模式可选)
python main.py                    # HTTP API 模式
python main.py --deep             # 启用深度思考
python main.py --stdio --deep     # STDIO 命令行模式
python main.py --hybrid --deep    # 混合模式 (API + STDIO)
```

Agent 将在 `http://localhost:8000` 启动。

### 2. 启动 LangGraph Studio (可选)

```bash
cd agent
langgraph dev
```

访问 https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024

### 3. 启动 Java 后端

```bash
cd backend

# 使用 Maven 构建并运行
mvn spring-boot:run

# 或者先打包再运行
mvn clean package
java -jar target/chatbot-backend-1.0.0.jar
```

后端将在 `http://localhost:9090` 启动。

### 4. 启动前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端将在 `http://localhost:5173` 启动。

## 🧠 深度思考 (Tree-of-Thoughts)

### 工作原理

```
用户问题
    ↓
生成多个思考分支 (默认3个)
    ↓
对每个分支进行评分
    ↓
选择最佳路径继续深入
    ↓
迭代指定深度 (默认2层)
    ↓
返回最优推理结果
```

### 使用方式

1. **前端界面**: 点击 🧠 深度思考开关
2. **API 调用**: 设置 `deep_think: true`
3. **命令行**: `python main.py --deep`

### 参数配置

| 参数 | 说明 | 默认值 |
|-----|------|--------|
| `--deep` | 启用深度思考 | false |
| `--branches` | 思考分支数 | 3 |
| `--depth` | 思考深度 | 2 |

## 📡 API 文档

### Java 后端 API (Port: 9090)

| 方法 | 路径 | 描述 |
|-----|------|------|
| POST | `/api/chat` | 发送聊天消息 |
| GET | `/api/chat/stats` | 获取记忆统计 |
| POST | `/api/chat/memory/clear-short-term` | 清除短期记忆 |
| POST | `/api/chat/memory/clear-all` | 清除所有记忆 |
| GET | `/api/chat/health` | 健康检查 |

### 请求示例

**发送消息 (含深度思考)**
```bash
curl -X POST http://localhost:9090/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "message": "分析一下人工智能的发展趋势",
    "sessionId": "default",
    "deepThink": true,
    "thoughtBranches": 3,
    "thoughtDepth": 2
  }'
```

### Python Agent API (Port: 8000)

| 方法 | 路径 | 描述 |
|-----|------|------|
| POST | `/api/chat` | 对话接口 |
| GET | `/api/stats` | 获取记忆统计 |
| POST | `/api/memory/clear-short-term` | 清除短期记忆 |
| POST | `/api/memory/clear-all` | 清除所有记忆 |
| GET | `/health` | 健康检查 |

## 🧠 功能特性

### 双层记忆系统

| 记忆类型 | 实现方式 | 特点 |
|---------|---------|------|
| **短时记忆** | `ConversationBufferWindowMemory` | 当前会话上下文，保留最近10轮 |
| **长时记忆** | `ChromaDB` + 向量检索 | 持久化存储，语义搜索 |

### LangGraph 工具集

| 工具 | 功能 | 触发方式 |
|-----|------|---------|
| 🌐 **网络搜索** | DuckDuckGo 实时搜索 | 询问时事、新闻、最新信息 |
| 📁 **文件操作** | 读写文件、目录管理 | 请求分析文件、保存内容 |
| 🧮 **数学计算** | 复杂数学运算 | 数学问题、计算请求 |
| 🧠 **深度思考** | TOT 多分支推理 | 开启深度思考开关 |

### 自动事实提取

系统会自动从对话中提取关键信息：
- 用户名字
- 年龄
- 居住地
- 喜好/厌恶
- 职业
- 生日

## ⚙️ 配置说明

### Java 后端配置 (`backend/src/main/resources/application.yml`)

```yaml
server:
  port: 9090

python-agent:
  base-url: http://localhost:8000
  timeout: 180000  # 3分钟，支持深度思考

spring:
  datasource:
    url: jdbc:mysql://localhost:3306/chatbot
    username: root
    password: your_password
```

### Python Agent 配置 (`agent/.env`)

```env
# DeepSeek API 配置
OPENAI_API_KEY=your_deepseek_api_key
OPENAI_BASE_URL=https://api.deepseek.com

# Agent 配置
AGENT_PORT=8000
```

### 前端配置 (`frontend/vite.config.js`)

```javascript
export default defineConfig({
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:9090',
        changeOrigin: true,
      }
    }
  }
})
```

## 🛠️ 开发指南

### 后端开发

```bash
cd backend

# 运行测试
mvn test

# 代码格式化
mvn spotless:apply

# 构建生产版本
mvn clean package -DskipTests
```

### 前端开发

```bash
cd frontend

# 开发模式
npm run dev

# 构建生产版本
npm run build

# 预览生产构建
npm run preview
```

## 📝 技术栈

### 后端
- Java 21
- Spring Boot 3.2
- Spring WebFlux (WebClient)
- Spring Security + JWT
- MySQL 8.0
- Flyway (数据库迁移)
- Lombok

### Python Agent
- **Python 3.13+** (推荐) / Python 3.11+
- FastAPI + Uvicorn
- LangChain + LangGraph
- LangGraph Studio (可视化调试)
- ChromaDB (向量数据库)
- **PyTorch 2.6.0** (针对Python 3.13优化)
- **sentence-transformers 3.0.1** (兼容性锁定)
- Tree-of-Thoughts (TOT深度推理)
- OpenTelemetry 1.38.0 (链路追踪)
- HuggingFace Embeddings

### 前端
- Vue 3
- Vite 5
- Axios (超时180秒支持深度思考)
- Marked (Markdown 渲染)
- DOMPurify (XSS 防护)

## 🔗 原版 LangChain 架构

```
┌─────────────────────────────────────────────────────────────┐
│                    ChatbotWithMemory                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              LangChain LCEL Chain                    │    │
│  │                                                      │    │
│  │   ChatPromptTemplate                                 │    │
│  │         │                                            │    │
│  │         ▼                                            │    │
│  │   ┌───────────────┐                                  │    │
│  │   │ System Prompt │ ← 基础人设                       │    │
│  │   ├───────────────┤                                  │    │
│  │   │ Memory Context│ ← 向量检索的长时记忆             │    │
│  │   ├───────────────┤                                  │    │
│  │   │ Chat History  │ ← ConversationBufferWindowMemory │    │
│  │   ├───────────────┤                                  │    │
│  │   │ User Input    │ ← 当前用户输入                   │    │
│  │   └───────────────┘                                  │    │
│  │         │                                            │    │
│  │         ▼                                            │    │
│  │   ChatOpenAI (DeepSeek)                              │    │
│  │         │                                            │    │
│  │         ▼                                            │    │
│  │   StrOutputParser                                    │    │
│  │         │                                            │    │
│  │         ▼                                            │    │
│  │   Response String                                    │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌─────────────────┐      ┌─────────────────────────┐       │
│  │   短时记忆       │      │      长时记忆            │       │
│  │ Conversation    │      │   MemoryStore           │       │
│  │ BufferWindow    │      │   (LangChain + Chroma)  │       │
│  │ Memory          │      │                          │       │
│  └─────────────────┘      └─────────────────────────┘       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## 安装

```bash
cd chatbot-with-memory
pip install -r requirements.txt
```

## 配置

创建 `.env` 文件：

```bash
# DeepSeek API配置
OPENAI_API_KEY=your_deepseek_api_key_here
OPENAI_BASE_URL=https://api.deepseek.com
```

## 使用方法

### 命令行交互

```bash
python chatbot.py
```

### 程序化调用

```python
from chatbot import ChatbotWithMemory

# 创建机器人
bot = ChatbotWithMemory(
    api_key="your-api-key",
    base_url="https://api.deepseek.com",
    model="deepseek-chat",
    memory_dir="./my_memory_db"
)

# 对话
response = bot.chat("你好，我叫张三")
print(response)

# 获取 Retriever 用于 RAG
retriever = bot.get_retriever()
```

### 使用 LangChain Retriever

```python
from memory_store import MemoryStore

# 初始化记忆存储
memory = MemoryStore(persist_directory="./memory_db")

# 获取 LangChain Retriever
retriever = memory.get_retriever(search_kwargs={"k": 5})

# 可以用于 RAG 链
from langchain.chains import RetrievalQA
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever
)
```

## 核心组件

### MemoryStore (memory_store.py)

基于 LangChain 封装的向量存储：

```python
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

# 使用 LangChain 组件
self.embeddings = HuggingFaceEmbeddings(model_name="...")
self.vectorstore = Chroma(embedding_function=self.embeddings, ...)
```

**主要方法：**
- `add_memory()` - 添加对话记忆
- `add_fact()` - 添加事实记忆
- `search_memories()` - 语义搜索
- `get_retriever()` - 获取 LangChain Retriever

### ChatbotWithMemory (chatbot.py)

使用 LangChain LCEL 构建的对话链：

```python
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.memory import ConversationBufferWindowMemory

# LCEL 链
self.chain = self.prompt | self.llm | StrOutputParser()
```

## 交互命令

| 命令 | 说明 |
|------|------|
| `quit` / `exit` | 退出程序 |
| `clear` | 清空短时记忆 |
| `stats` | 查看记忆统计 |
| `forget` | 清空所有记忆 |

## 与原版对比

| 特性 | 原版 | LangChain 版 |
|------|------|-------------|
| LLM调用 | OpenAI SDK | `ChatOpenAI` |
| 短时记忆 | 手动 List | `ConversationBufferWindowMemory` |
| 向量存储 | 直接 ChromaDB | `langchain_community.vectorstores.Chroma` |
| 嵌入模型 | SentenceTransformer | `HuggingFaceEmbeddings` |
| 对话链 | 手动构建 | LCEL (`prompt | llm | parser`) |
| RAG支持 | 无 | `get_retriever()` |

## 扩展能力

使用 LangChain 后，可以轻松扩展：

1. **RAG 问答**：使用 `RetrievalQA` 链
2. **Agent 工具**：将记忆检索作为 Tool
3. **多模型切换**：轻松切换不同 LLM
4. **流式输出**：使用 `stream()` 方法
5. **回调监控**：添加 LangChain Callbacks

## 🔧 故障排除

### Python 3.13 Meta Tensor 错误

**错误信息：**
```
NotImplementedError: Cannot copy out of meta tensor; no data!
```

**原因：** PyTorch 2.9.1 + sentence-transformers 5.x 在 Python 3.13 上存在兼容性问题

**解决方案：**
```bash
pip install torch==2.6.0 sentence-transformers==3.0.1
```

### OpenTelemetry 版本冲突

**错误信息：**
```
opentelemetry-instrumentation-asgi 0.53b0 requires opentelemetry-api~=1.32
```

**解决方案：** 锁定所有 OpenTelemetry 版本为 1.38.0：
```
opentelemetry-api==1.38.0
opentelemetry-sdk==1.38.0
opentelemetry-instrumentation==0.59b0
```

### 深度思考请求超时

**错误信息：** 前端显示 "发送失败，请检查网络"

**原因：** 深度思考 (TOT) 需要较长时间，默认60秒超时不够

**解决方案：**
1. 前端 `chat.js` 超时设为 180000ms
2. 后端 `application.yml` 中 `python-agent.timeout` 设为 180000

### LangGraph Studio 无法启动

确保安装了正确版本：
```bash
pip install "langgraph-cli[inmem]"
langgraph dev --host 0.0.0.0 --port 2024
```

## 许可证

MIT License
"# chatsystem" 
