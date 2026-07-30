# AI 智能商城（AI Mall）

一个具备 RAG（检索增强生成）能力的智能商城：用户可通过自然语言搜索商品，并获得 AI 导购的个性化推荐。

## 技术栈

| 层 | 技术 |
|----|------|
| 后端 | FastAPI（异步）+ SQLAlchemy 2.0（MySQL 异步）+ Chroma 向量库 + 智谱 GLM-4.5-Air |
| 前端 | Vue 3（`<script setup>`）+ Vite + Tailwind CSS + Pinia + Axios |
| 数据库 | MySQL 8.0（业务库）+ Chroma（向量库，嵌入式无需独立服务） |
| 可选 | Redis + Celery（异步索引任务，**默认不启用也可完整运行**） |

## 目录结构

```
.
├── backend/               # FastAPI 后端
│   ├── app/
│   │   ├── api/v1/        # 商品/搜索/对话/购物车 接口
│   │   ├── core/          # 数据库/Redis/Chroma/LLM 客户端
│   │   ├── models/        # SQLAlchemy 模型
│   │   ├── schemas/       # Pydantic 数据模型
│   │   ├── services/      # 业务服务层 + RAG 核心
│   │   └── tasks/         # Celery 异步任务（可选）
│   ├── docker-compose.yml # MySQL + Redis
│   ├── requirements.txt
│   └── seed_data.py       # 种子数据脚本
└── frontend/              # Vue 3 前端
    └── src/
        ├── components/    # 导航栏/商品卡/AI 对话/搜索结果
        ├── views/         # 首页/详情/购物车
        ├── api/           # Axios 封装 + SSE 流式
        └── stores/        # Pinia 购物车
```

## 环境准备

### 必需
- **Python 3.10+**（推荐用 conda 创建虚拟环境）
- **Node.js 18+**（前端构建）
- **MySQL 8.0**（业务数据库）
- **智谱 AI API Key**（用于 LLM 对话与向量嵌入，在 [open.bigmodel.cn](https://open.bigmodel.cn) 获取）

### 可选
- **Redis**（仅在启用 Celery 异步索引时需要，默认配置下无需启动 Redis）
- **Docker**（用于快速启动 MySQL）

## 启动步骤

### 1. 启动 MySQL

**方式 A：用 Docker Compose（推荐）**

```bash
cd backend
docker compose up -d
```

会启动 MySQL 8.0（账号 `root` / 密码 `root` / 数据库 `ai_mall`）。

**方式 B：本地已安装 MySQL**

手动创建数据库即可：

```sql
CREATE DATABASE ai_mall CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 2. 配置后端环境变量

```bash
cd backend
cp .env.example .env
```

编辑 `.env`，**必须**填入你的智谱 API Key：

```env
ZHIPU_API_KEY=你的真实智谱API密钥
```

若你的 MySQL 密码不是 `root`，同步修改 `DATABASE_URL`。

### 3. 安装后端依赖并启动

```bash
cd backend
pip install -r requirements.txt

# 初始化种子数据（插入 10 件示例商品 + 构建向量索引）
python seed_data.py

# 启动后端（开发模式，热重载）
python -m uvicorn app.main:app --reload --port 8000
```

启动成功后：
- 健康检查：http://localhost:8000
- API 文档：http://localhost:8000/docs

### 4. 启动前端

**另开一个终端**：

```bash
cd frontend
npm install
npm run dev
```

### 5. 访问应用

浏览器打开 **http://localhost:5173** 即可。

> ⚠️ 请用 `localhost` 访问，不要用 `127.0.0.1`，否则可能触发 CORS 问题。

## 功能体验

- **商品浏览**：首页网格展示，支持分类筛选
- **AI 语义搜索**：顶部搜索框输入自然语言（如「适合冬天的轻薄羽绒服」），后端通过 RAG 返回语义匹配商品 + AI 推荐语
- **AI 导购对话**：右下角悬浮按钮，多轮流式对话（打字机效果）
- **商品详情**：大图、规格、价格，可「加入购物车」或「问 AI」
- **购物车**：增删改数量、模拟结算

## 常见问题

### 1. 后端启动卡在「数据库表已就绪」之后不动

Chroma 首次启动会下载默认 embedding 模型（约 90MB），网络慢时可能卡住。代码已加 60 秒超时保护，超时后后端会照常启动，Chroma 在后台继续下载。

若仍卡死，可设置国内镜像后重启：

```bash
# Windows PowerShell
$env:HF_ENDPOINT="https://hf-mirror.com"
python -m uvicorn app.main:app --reload --port 8000
```

### 2. 前端「网络异常，请检查连接」

- 确认后端已完全启动（日志出现 `Application startup complete`）
- 确认用 `http://localhost:5173` 访问，而非 `127.0.0.1`
- 前端 `src/api/index.js` 的 `BASE_URL` 应为 `/api/v1`（相对路径，走 Vite 代理）

### 3. AI 对话/搜索报错或无响应

- 检查 `.env` 中 `ZHIPU_API_KEY` 是否为真实密钥
- 检查智谱账户是否有余额
- 未配置 Key 时，商品 CRUD 和购物车仍可用，但 AI 功能不可用

### 4. `seed_data.py` 报错

- 确认 MySQL 已启动且 `ai_mall` 数据库已创建
- 确认 `ZHIPU_API_KEY` 已配置（构建向量索引需调用 embedding 接口）
- 商品已存在时会自动跳过，可重复执行

### 5. PyCharm 运行 uvicorn 报 `No such file or directory`

PyCharm 运行配置需把 **Script path** 切换为 **Module name**，填 `uvicorn`，参数 `app.main:app --reload --port 8000`。或直接在终端用 `python -m uvicorn app.main:app --reload --port 8000`。

### 6. `chromadb` 安装失败

```bash
pip install chromadb --prefer-binary
```

### 7. 是否需要启动 Redis

**不需要**。当前配置下，商品写入时通过 `rag_service` 直接异步同步向量索引到 Chroma，不依赖 Redis/Celery。

如需启用 Celery 异步索引（高并发场景），启动 Redis 后另开终端运行：

```bash
# Windows 需加 --pool=solo
celery -A app.celery_app worker --loglevel=info --pool=solo
```

## 启动顺序速查

```
1. docker compose up -d          # 启动 MySQL
2. cp .env.example .env          # 配置 ZHIPU_API_KEY
3. pip install -r requirements.txt
4. python seed_data.py           # 初始化数据
5. python -m uvicorn app.main:app --reload --port 8000   # 启动后端
6. cd ../frontend && npm install && npm run dev          # 启动前端
7. 浏览器打开 http://localhost:5173
```

## 接口一览

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/products` | 商品列表（支持 category/skip/limit） |
| GET | `/api/v1/products/{id}` | 商品详情 |
| POST | `/api/v1/products` | 创建商品 |
| PUT | `/api/v1/products/{id}` | 更新商品 |
| DELETE | `/api/v1/products/{id}` | 删除商品 |
| POST | `/api/v1/search/semantic` | 语义搜索（RAG） |
| POST | `/api/v1/chat/stream` | AI 流式对话（SSE） |
| POST | `/api/v1/cart/checkout` | 购物车结算 |
