# CLAUDE.md - 情侣小空间 APP 架构文档

## 项目概述
情侣专属的私密数字空间，支持实时互动、数据同步和联网功能。

## 目录结构

```
小空间/
├── backend/                    # FastAPI 后端服务
│   ├── src/
│   │   ├── api/               # API 路由层
│   │   │   ├── v1/           # API 版本 1
│   │   │   │   ├── auth.py   # 认证相关 API
│   │   │   │   ├── users.py  # 用户相关 API
│   │   │   │   ├── chat.py   # 聊天相关 API
│   │   │   │   ├── photos.py # 相册相关 API
│   │   │   │   ├── diaries.py # 日记相关 API
│   │   │   │   └── todos.py  # 待办相关 API
│   │   │   └── dependencies.py # 依赖注入（认证等）
│   │   ├── core/             # 核心配置
│   │   │   ├── config.py     # 配置管理
│   │   │   ├── security.py   # 安全相关（JWT、密码）
│   │   │   └── database.py   # 数据库连接
│   │   ├── models/           # SQLAlchemy 数据模型
│   │   │   ├── user.py       # 用户模型
│   │   │   ├── couple.py     # 情侣关系模型
│   │   │   ├── room.py       # 聊天房间模型
│   │   │   ├── message.py    # 消息模型
│   │   │   ├── photo.py      # 照片模型
│   │   │   ├── diary.py      # 日记模型
│   │   │   └── todo.py       # 待办模型
│   │   ├── schemas/          # Pydantic 请求/响应模型
│   │   │   ├── auth.py       # 认证相关 Schema
│   │   │   ├── user.py       # 用户相关 Schema
│   │   │   ├── chat.py       # 聊天相关 Schema
│   │   │   ├── photo.py      # 照片相关 Schema
│   │   │   ├── diary.py      # 日记相关 Schema
│   │   │   └── todo.py       # 待办相关 Schema
│   │   ├── services/         # 业务逻辑层
│   │   │   ├── auth_service.py    # 认证服务
│   │   │   ├── user_service.py    # 用户服务
│   │   │   ├── chat_service.py    # 聊天服务
│   │   │   ├── photo_service.py   # 相册服务
│   │   │   ├── diary_service.py   # 日记服务
│   │   │   ├── todo_service.py    # 待办服务
│   │   │   └── storage_service.py # 对象存储服务
│   │   ├── websocket/        # Socket.IO 实时通信
│   │   │   ├── handler.py    # Socket.IO 事件处理
│   │   │   └── manager.py    # 连接管理
│   │   ├── utils/            # 工具函数
│   │   │   ├── image.py      # 图片处理
│   │   │   ├── notification.py # 推送通知
│   │   │   └── logger.py     # 日志工具
│   │   └── main.py           # 应用入口
│   ├── alembic/              # 数据库迁移
│   ├── tests/                # 测试
│   ├── requirements.txt       # Python 依赖
│   ├── Dockerfile            # Docker 镜像构建
│   └── .env.example          # 环境变量示例
│
├── frontend/                  # React Native 前端
│   ├── src/
│   │   ├── screens/          # 页面组件
│   │   │   ├── auth/         # 认证相关页面
│   │   │   │   ├── LoginScreen.tsx
│   │   │   │   ├── RegisterScreen.tsx
│   │   │   │   └── CoupleBindScreen.tsx
│   │   │   ├── chat/         # 聊天相关页面
│   │   │   │   └── ChatScreen.tsx
│   │   │   ├── album/        # 相册相关页面
│   │   │   │   ├── AlbumListScreen.tsx
│   │   │   │   └── PhotoDetailScreen.tsx
│   │   │   ├── diary/        # 日记相关页面
│   │   │   │   ├── DiaryListScreen.tsx
│   │   │   │   └── DiaryDetailScreen.tsx
│   │   │   ├── todo/         # 待办相关页面
│   │   │   │   └── TodoScreen.tsx
│   │   │   └── profile/      # 个人资料页面
│   │   │       └── ProfileScreen.tsx
│   │   ├── components/       # 可复用组件
│   │   │   ├── common/       # 通用组件
│   │   │   │   ├── Button.tsx
│   │   │   │   ├── Input.tsx
│   │   │   │   ├── Card.tsx
│   │   │   │   └── Modal.tsx
│   │   │   ├── chat/         # 聊天组件
│   │   │   │   ├── MessageBubble.tsx
│   │   │   │   └── ChatInput.tsx
│   │   │   └── photo/        # 照片组件
│   │   │       └── PhotoGrid.tsx
│   │   ├── navigation/       # 导航配置
│   │   │   ├── AppNavigator.tsx
│   │   │   └── TabNavigator.tsx
│   │   ├── store/            # Redux 状态管理
│   │   │   ├── index.ts
│   │   │   ├── authSlice.ts   # 认证状态
│   │   │   ├── chatSlice.ts  # 聊天状态
│   │   │   ├── userSlice.ts  # 用户状态
│   │   │   └── themeSlice.ts # 主题状态
│   │   ├── services/         # API 服务
│   │   │   ├── api.ts        # API 客户端
│   │   │   ├── authService.ts
│   │   │   ├── userService.ts
│   │   │   └── storageService.ts
│   │   ├── hooks/            # 自定义 Hooks
│   │   │   ├── useAuth.ts
│   │   │   └── useSocket.ts
│   │   ├── utils/            # 工具函数
│   │   │   ├── date.ts       # 日期处理
│   │   │   └── storage.ts    # 本地存储
│   │   ├── theme/            # 主题配置
│   │   │   ├── colors.ts
│   │   │   └── typography.ts
│   │   ├── types/            # TypeScript 类型定义
│   │   │   ├── auth.ts
│   │   │   ├── user.ts
│   │   │   └── chat.ts
│   │   └── App.tsx           # 应用入口
│   ├── package.json
│   ├── app.json
│   ├── tsconfig.json
│   └── Dockerfile
│
├── memory-bank/              # 项目文档与记忆库
│   ├── project-context.md    # 项目上下文
│   ├── tech-stack.md         # 技术栈
│   ├── implementation-plan.md # 实施计划
│   ├── progress.md           # 进度记录
│   └── architecture.md       # 本文档（架构说明）
│
├── docs/                     # 项目文档
│   ├── api.md                # API 文档
│   ├── deployment.md         # 部署文档
│   └── development.md        # 开发指南
│
├── docker-compose.yml        # Docker 容器编排
├── .gitignore
├── LICENSE
└── README.md
```

## 架构分层

### 后端架构（Layered Architecture）

```
┌─────────────────────────────────────┐
│      API Layer (路由层)              │  /api/v1/*
├─────────────────────────────────────┤
│    Service Layer (业务逻辑层)         │  services/
├─────────────────────────────────────┤
│      Model Layer (数据访问层)        │  models/
├─────────────────────────────────────┤
│    Database Layer (数据库层)         │  PostgreSQL
└─────────────────────────────────────┘
```

### 数据流向

```
Frontend (React Native)
    ↓ HTTP/JSON
API Layer (FastAPI)
    ↓ 调用
Service Layer (业务逻辑)
    ↓ ORM
Model Layer (SQLAlchemy)
    ↓ SQL
PostgreSQL
```

### 实时通信流向

```
Frontend (socket.io-client)
    ↓ WebSocket
Socket.IO Server (FastAPI)
    ↓ 广播/单播
Connected Clients
```

## 模块职责

| 模块 | 职责 |
|------|------|
| `api/` | HTTP 路由定义，请求验证，响应格式化 |
| `core/` | 全局配置，安全工具，数据库连接池 |
| `models/` | 数据库表定义，ORM 关系映射 |
| `schemas/` | Pydantic 数据模型，请求/响应验证 |
| `services/` | 业务逻辑封装，事务处理 |
| `websocket/` | Socket.IO 连接管理，实时消息处理 |
| `utils/` | 工具函数，辅助功能 |

## 依赖关系

```
api/  →  services/  →  models/  →  database
       ↓
   schemas/ (数据验证)
       ↓
   core/ (配置与安全)
```

## 技术选型理由

| 技术栈 | 理由 |
|--------|------|
| FastAPI | 快速开发，原生异步，自动文档 |
| PostgreSQL | 关系型数据，ACID 事务，全文搜索 |
| Redis | 高性能缓存，发布/订阅，会话存储 |
| Socket.IO | 实时通信，自动降级，房间机制 |
| React Native + Expo | 跨平台，热更新，丰富组件 |
| Redux Toolkit | 状态管理，DevTools 支持 |

## 安全设计

1. **认证**：JWT Access Token + Refresh Token
2. **授权**：情侣关系验证，数据隔离
3. **传输**：HTTPS 加密
4. **存储**：敏感数据加密（密码 bcrypt）
5. **限流**：API 频率限制防止滥用

## 性能优化

1. **数据库**：索引优化，连接池，查询优化
2. **缓存**：Redis 缓存热点数据
3. **异步**：FastAPI 异步处理 I/O
4. **前端**：图片懒加载，虚拟列表，请求缓存

## 部署架构

```
Nginx (反向代理 / SSL)
    ↓
FastAPI (应用服务器)
    ↓
PostgreSQL + Redis (数据层)
    ↓
Object Storage (文件存储)
```

## 开发规范

- Python 代码遵循 PEP 8
- 使用类型注解（Type Hints）
- API 路由命名清晰，使用 RESTful 风格
- 错误信息统一格式
- 日志记录关键操作

## 扩展点

- 可添加 AI 助手服务
- 可集成第三方登录（微信、Google）
- 可添加数据分析与可视化
- 可扩展为多用户社交功能

---

**版本：** 1.0
**更新日期：** 2025-12-23
