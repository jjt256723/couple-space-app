# 情侣小空间 APP

情侣专属的私密数字空间，支持实时互动、数据同步和联网功能。

## 功能特性

- 实时聊天
- 情侣相册
- 共享日记
- 待办事项
- 重要日期提醒
- 主题定制

## 技术栈

### 后端
- FastAPI + Python 3.11
- PostgreSQL + Redis
- Socket.IO 实时通信
- 对象存储（OSS/COS/S3）

### 前端
- React Native + Expo
- Redux Toolkit 状态管理
- Socket.IO 客户端

## 快速开始

### 环境要求
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Git

### 1. 克隆项目
```bash
git clone <repository-url>
cd 小空间
```

### 2. 启动开发环境
```bash
docker-compose up -d
```

这将启动以下服务：
- PostgreSQL 数据库 (端口 5432)
- Redis 缓存 (端口 6379)
- FastAPI 后端 (端口 8000)

### 3. 后端开发

安装依赖（本地开发）：
```bash
cd backend
pip install -r requirements.txt
```

运行后端：
```bash
uvicorn src.main:app --reload
```

### 4. 前端开发

安装依赖：
```bash
cd frontend
npm install
```

运行前端：
```bash
npm start
```

## 项目结构

```
小空间/
├── backend/              # FastAPI 后端
│   ├── src/
│   │   ├── api/         # API 路由
│   │   ├── core/        # 核心配置
│   │   ├── models/      # 数据模型
│   │   ├── schemas/     # Pydantic 模型
│   │   └── services/    # 业务逻辑
│   └── requirements.txt
├── frontend/             # React Native 前端
│   └── src/
│       ├── screens/     # 页面
│       ├── components/  # 组件
│       └── store/       # Redux 状态
├── memory-bank/         # 项目文档
└── docker-compose.yml   # 容器编排
```

## 开发进度

详见 [memory-bank/progress.md](memory-bank/progress.md)

## 文档

- [项目上下文](memory-bank/project-context.md)
- [技术栈](memory-bank/tech-stack.md)
- [实施计划](memory-bank/implementation-plan.md)
- [架构文档](memory-bank/architecture.md)

## License

MIT
