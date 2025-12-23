# 情侣小空间 APP - 技术栈推荐

## 技术栈方案

### 前端（移动端 + Web）

#### 方案：React Native + Expo（推荐）

**理由：**
- 跨平台开发，一套代码支持 iOS 和 Android
- 热更新支持，快速迭代
- 丰富的社区生态和组件库
- 支持原生模块扩展

**核心依赖：**
```json
{
  "expo": "^50.0.0",
  "react": "^18.2.0",
  "react-native": "^0.73.0",
  "socket.io-client": "^4.6.0",
  "@react-navigation/native": "^6.1.0",
  "@reduxjs/toolkit": "^2.0.0",
  "axios": "^1.6.0",
  "expo-image-picker": "^14.7.0",
  "expo-notifications": "^0.27.0",
  "react-native-gesture-handler": "^2.14.0",
  "@react-native-async-storage/async-storage": "^1.21.0"
}
```

**替代方案：**
- Flutter（性能更好，学习曲线较陡）
- 纯 Web + PWA（功能受限，但最简单）

---

### 后端

#### 方案：FastAPI + Python 3.11（推荐）

**理由：**
- 开发速度快，代码简洁
- 原生支持异步
- 自动生成 OpenAPI 文档
- 类型安全，Pydantic 数据校验
- 丰富的生态系统

**核心依赖：**
```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.25
alembic==1.13.0
psycopg2-binary==2.9.9
redis==5.0.1
python-socketio==5.11.0
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
pydantic==2.5.3
pydantic-settings==2.1.0
```

**替代方案：**
- Node.js + Express（JavaScript 全栈）
- Go + Gin（高性能）

---

### 实时通信

#### 方案：Python-SocketIO + Socket.IO Client

**理由：**
- 支持 WebSocket 和 HTTP 长轮询自动降级
- 实现房间（Room）机制，适合情侣一对一聊天
- 自动重连、心跳检测
- 支持二进制数据传输（图片）

**功能：**
- 实时聊天消息
- 在线状态同步
- 数据变更通知
- 推送通知

---

### 数据库

#### 方案：PostgreSQL + Redis

**PostgreSQL（主数据库）：**
```sql
-- 主要存储
- 用户账号与关系
- 聊天消息记录
- 相册照片元数据
- 日记、待办事项
- 系统配置
```

**Redis（缓存与会话）：**
```
- 用户会话 Token
- 在线用户列表
- 消息队列（推送队列）
- 实时状态缓存
- 频率限制
```

**理由：**
- PostgreSQL：关系型数据，ACID 事务，全文搜索
- Redis：高性能缓存，支持发布/订阅

---

### 文件存储

#### 方案：对象存储服务（推荐）

**选项：**
- 阿里云 OSS（国内）
- 腾讯云 COS（国内）
- AWS S3（国际）
- MinIO（自建，可选）

**存储内容：**
- 用户头像
- 相册照片
- 附件文件

**理由：**
- 无限扩展存储空间
- CDN 加速
- 自动备份
- 成本可控

---

### 部署架构

#### 方案：Docker + Docker Compose

**开发环境：**
```yaml
services:
  frontend:    # React Native 开发服务器
  backend:     # FastAPI 后端
  postgres:    # PostgreSQL 数据库
  redis:       # Redis 缓存
  nginx:       # 反向代理
```

**生产环境：**
- 云服务器（阿里云 ECS / 腾讯云 CVM）
- 或 Serverless（阿里云 FC / 腾讯云 SCF）

---

### 安全方案

#### 认证与授权
- JWT Token 认证
- Refresh Token 刷新机制
- 情侣关系验证

#### 数据安全
- HTTPS 加密传输
- 敏感数据加密存储
- API 频率限制
- 输入参数校验

---

### 监控与日志

#### 方案
- **日志：** Python Logging + Loguru
- **监控：** Prometheus + Grafana（可选）
- **错误追踪：** Sentry（可选）

---

## 技术栈总结

| 层级 | 技术 | 版本 |
|------|------|------|
| 前端 | React Native + Expo | 0.73+ |
| 后端 | FastAPI + Python | 0.109+ / 3.11+ |
| 实时通信 | Socket.IO | 5.11+ |
| 数据库 | PostgreSQL | 15+ |
| 缓存 | Redis | 7.0+ |
| 文件存储 | 对象存储 (OSS/COS/S3) | - |
| 容器化 | Docker + Compose | - |
| 部署 | 云服务器 / Serverless | - |

---

## 架构图

```
┌─────────────────────────────────────────────────────────┐
│                      用户层                              │
│  iOS App  │  Android App  │  Web 浏览器（可选）          │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                    API 网关 (Nginx)                       │
│         负载均衡 / SSL 终止 / 静态资源服务               │
└─────────────────────────────────────────────────────────┘
                            ↓
        ┌───────────────────┴───────────────────┐
        ↓                                       ↓
┌─────────────────────┐            ┌─────────────────────────────┐
│  FastAPI 后端       │            │  Socket.IO 实时服务          │
│  - REST API         │◄──────────►│  - 实时聊天                 │
│  - 用户认证         │            │  - 在线状态                 │
│  - 业务逻辑         │            │  - 推送通知                 │
└─────────────────────┘            └─────────────────────────────┘
        ↓                                       ↓
┌─────────────────────┐            ┌─────────────────────────────┐
│  PostgreSQL         │            │  Redis                       │
│  - 用户数据         │            │  - 会话缓存                 │
│  - 聊天记录         │            │  - 在线状态                 │
│  - 相册/日记        │            │  - 消息队列                 │
└─────────────────────┘            └─────────────────────────────┘
        ↓
┌─────────────────────┐
│  对象存储 (OSS)     │
│  - 头像/照片        │
└─────────────────────┘
```

---

## 开发环境要求

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Git
- IDE（VS Code / PyCharm / WebStorm）

---

## 项目结构建议

```
小空间/
├── backend/              # FastAPI 后端
│   ├── src/
│   │   ├── api/         # API 路由
│   │   ├── core/        # 核心配置
│   │   ├── models/      # 数据模型
│   │   ├── schemas/     # Pydantic 模型
│   │   ├── services/    # 业务逻辑
│   │   └── websocket/   # Socket.IO 处理
│   ├── alembic/         # 数据库迁移
│   └── tests/           # 测试
├── frontend/            # React Native 前端
│   ├── src/
│   │   ├── screens/     # 页面
│   │   ├── components/  # 组件
│   │   ├── navigation/  # 导航
│   │   ├── store/       # Redux 状态
│   │   └── utils/       # 工具
├── docker-compose.yml   # 容器编排
└── memory-bank/         # 文档目录
```
