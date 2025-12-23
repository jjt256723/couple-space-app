#!/bin/bash

# ================================================
# 情侣小空间 APP - 阿里云服务器部署脚本
# 系统: Alibaba Cloud Linux 3 / CentOS 8+
# 作者: 自动生成
# ================================================

set -e  # 遇到错误立即退出

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 项目配置
PROJECT_DIR="/opt/couple-space-app"
GITHUB_REPO="https://github.com/jjt256723/couple-space-app.git"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  情侣小空间 APP - 自动部署脚本${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# ================================================
# 步骤 1: 更新系统
# ================================================
echo -e "${YELLOW}[1/8] 更新系统...${NC}"
sudo dnf update -y
echo -e "${GREEN}✓ 系统更新完成${NC}"
echo ""

# ================================================
# 步骤 2: 安装基础工具
# ================================================
echo -e "${YELLOW}[2/8] 安装基础工具...${NC}"
sudo dnf install -y git curl vim htop net-tools
echo -e "${GREEN}✓ 基础工具安装完成${NC}"
echo ""

# ================================================
# 步骤 3: 安装 Docker
# ================================================
echo -e "${YELLOW}[3/8] 安装 Docker...${NC}"

if ! command -v docker &> /dev/null; then
    # 添加 Docker 官方仓库
    sudo dnf config-manager --add-repo=https://download.docker.com/linux/centos/docker-ce.repo

    # 安装 Docker
    sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

    # 启动 Docker
    sudo systemctl start docker
    sudo systemctl enable docker

    # 添加当前用户到 docker 组（可选）
    sudo usermod -aG docker $USER

    echo -e "${GREEN}✓ Docker 安装完成${NC}"
else
    echo -e "${GREEN}✓ Docker 已安装，跳过${NC}"
fi

# 验证 Docker
docker --version
echo ""

# ================================================
# 步骤 4: 配置防火墙（开放端口）
# ================================================
echo -e "${YELLOW}[4/8] 配置防火墙...${NC}"

if command -v firewall-cmd &> /dev/null; then
    sudo firewall-cmd --permanent --add-port=8000/tcp  # 后端 API
    sudo firewall-cmd --permanent --add-port=5432/tcp  # PostgreSQL（可选，用于外部访问）
    sudo firewall-cmd --reload
    echo -e "${GREEN}✓ 防火墙配置完成${NC}"
else
    echo -e "${YELLOW}⚠ 未检测到 firewalld，跳过防火墙配置${NC}"
fi

# 提示手动配置阿里云安全组
echo -e "${YELLOW}⚠ 请在阿里云控制台手动配置安全组:${NC}"
echo "   - 开放端口 8000（后端 API）"
echo "   - 如果需要数据库访问，开放 5432"
echo ""

# ================================================
# 步骤 5: 克隆项目
# ================================================
echo -e "${YELLOW}[5/8] 克隆项目...${NC}"

if [ -d "$PROJECT_DIR" ]; then
    echo -e "${YELLOW}⚠ 项目目录已存在，更新代码...${NC}"
    cd $PROJECT_DIR
    git pull origin main
else
    sudo mkdir -p $PROJECT_DIR
    sudo chown -R $USER:$USER $PROJECT_DIR
    git clone $GITHUB_REPO $PROJECT_DIR
    cd $PROJECT_DIR
fi

echo -e "${GREEN}✓ 项目代码准备完成${NC}"
echo ""

# ================================================
# 步骤 6: 配置环境变量
# ================================================
echo -e "${YELLOW}[6/8] 配置环境变量...${NC}"

if [ ! -f "backend/.env" ]; then
    cp backend/.env.example backend/.env

    # 生成随机密钥
    SECRET_KEY=$(openssl rand -hex 32)

    # 更新环境变量
    sed -i "s/your-secret-key-change-in-production/$SECRET_KEY/g" backend/.env
    sed -i "s|DATABASE_URL=.*|DATABASE_URL=postgresql+asyncpg://couple_space:$(openssl rand -hex 16)@postgres:5432/couple_space|g" backend/.env
    sed -i "s/development/production/g" backend/.env
    sed -i "s/DEBUG=True/DEBUG=False/g" backend/.env

    echo -e "${GREEN}✓ 环境变量配置完成${NC}"
    echo -e "${YELLOW}⚠ 请根据需要手动配置对象存储（OSS/COS）${NC}"
else
    echo -e "${GREEN}✓ 环境变量文件已存在，跳过${NC}"
fi
echo ""

# ================================================
# 步骤 7: 启动服务
# ================================================
echo -e "${YELLOW}[7/8] 启动服务...${NC}"

# 停止旧容器（如果有）
docker compose down 2>/dev/null || true

# 构建并启动
docker compose up -d --build

# 等待服务启动
echo -e "${YELLOW}等待服务启动...${NC}"
sleep 10

echo -e "${GREEN}✓ 服务启动完成${NC}"
echo ""

# ================================================
# 步骤 8: 健康检查
# ================================================
echo -e "${YELLOW}[8/8] 健康检查...${NC}"

# 检查后端 API
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ 后端服务正常${NC}"
else
    echo -e "${RED}✗ 后端服务未就绪${NC}"
    echo -e "${YELLOW}⚠ 请查看日志: docker compose logs${NC}"
fi

# 检查 PostgreSQL
if docker compose ps | grep -q "postgres.*Up"; then
    echo -e "${GREEN}✓ PostgreSQL 正常${NC}"
else
    echo -e "${RED}✗ PostgreSQL 未就绪${NC}"
fi

# 检查 Redis
if docker compose ps | grep -q "redis.*Up"; then
    echo -e "${GREEN}✓ Redis 正常${NC}"
else
    echo -e "${RED}✗ Redis 未就绪${NC}"
fi

echo ""

# ================================================
# 部署完成
# ================================================
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  部署完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}服务信息:${NC}"
echo "  - 后端 API: http://$(hostname -I | awk '{print $1}'):8000"
echo "  - API 文档: http://$(hostname -I | awk '{print $1}'):8000/docs"
echo "  - 项目目录: $PROJECT_DIR"
echo ""
echo -e "${YELLOW}常用命令:${NC}"
echo "  - 查看日志:    docker compose logs -f"
echo "  - 查看状态:    docker compose ps"
echo "  - 停止服务:    docker compose down"
echo "  - 重启服务:    docker compose restart"
echo "  - 进入容器:    docker compose exec backend bash"
echo ""
echo -e "${YELLOW}数据库迁移（首次运行）:${NC}"
echo "  docker compose exec backend alembic upgrade head"
echo ""
echo -e "${YELLOW}创建用户（测试）:${NC}"
echo "  curl -X POST http://$(hostname -I | awk '{print $1}'):8000/api/v1/auth/register \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"username\":\"test\",\"email\":\"test@example.com\",\"nickname\":\"测试\",\"password\":\"123456\"}'"
echo ""
