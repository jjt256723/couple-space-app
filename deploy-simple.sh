#!/bin/bash

# 情侣小空间 APP - 阿里云服务器部署脚本（国内镜像版）
set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  情侣小空间 APP - 自动部署脚本${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# 更新系统
echo -e "${YELLOW}[1/8] 更新系统...${NC}"
sudo dnf update -y
echo -e "${GREEN}✓ 系统更新完成${NC}"

# 安装基础工具
echo -e "${YELLOW}[2/8] 安装基础工具...${NC}"
sudo dnf install -y git curl vim htop net-tools yum-utils device-mapper-persistent-data lvm2
echo -e "${GREEN}✓ 基础工具安装完成${NC}"

# 配置 Docker 国内镜像源
echo -e "${YELLOW}[3/8] 配置 Docker...${NC}"

# 卸载旧版本
sudo dnf remove -y docker docker-client docker-client-latest docker-common docker-latest docker-latest-logrotate docker-logrotate docker-engine docker-ce docker-ce-cli containerd.io 2>/dev/null || true

# 使用阿里云 Docker 镜像源
sudo yum-config-manager --add-repo https://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo

# 安装 Docker
sudo dnf install -y docker-ce docker-ce-cli containerd.io

# 配置 Docker 镜像加速器
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json > /dev/null <<EOF
{
  "registry-mirrors": [
    "https://docker.m.daocloud.io",
    "https://dockerhub.azk8s.cn",
    "https://docker.mirrors.ustc.edu.cn"
  ]
}
EOF

# 启动 Docker
sudo systemctl start docker
sudo systemctl enable docker
sudo systemctl daemon-reload
sudo systemctl restart docker

# 验证 Docker
docker --version
echo -e "${GREEN}✓ Docker 安装完成${NC}"

# 配置防火墙
echo -e "${YELLOW}[4/8] 配置防火墙...${NC}"
if command -v firewall-cmd &> /dev/null; then
    sudo firewall-cmd --permanent --add-port=80/tcp
    sudo firewall-cmd --permanent --add-port=443/tcp
    sudo firewall-cmd --permanent --add-port=8000/tcp
    sudo firewall-cmd --reload
    echo -e "${GREEN}✓ 防火墙配置完成${NC}"
else
    echo -e "${YELLOW}⚠ 未检测到 firewalld${NC}"
fi

echo -e "${YELLOW}⚠ 请在阿里云控制台手动配置安全组:${NC}"
echo "   - 开放端口 80、443、8000"
echo ""

# 克隆项目
echo -e "${YELLOW}[5/8] 克隆项目...${NC}"
PROJECT_DIR="/opt/couple-space-app"

if [ -d "$PROJECT_DIR" ]; then
    echo -e "${YELLOW}⚠ 项目目录已存在，更新代码...${NC}"
    cd $PROJECT_DIR
    git pull origin main
else
    sudo mkdir -p $PROJECT_DIR
    sudo chown -R $USER:$USER $PROJECT_DIR
    git clone https://github.com/jjt256723/couple-space-app.git $PROJECT_DIR
    cd $PROJECT_DIR
fi
echo -e "${GREEN}✓ 项目代码准备完成${NC}"

# 配置环境变量
echo -e "${YELLOW}[6/8] 配置环境变量...${NC}"
if [ ! -f "backend/.env" ]; then
    cp backend/.env.example backend/.env
    SECRET_KEY=$(openssl rand -hex 32)
    sed -i "s/your-secret-key-change-in-production/$SECRET_KEY/g" backend/.env
    sed -i "s|DATABASE_URL=.*|DATABASE_URL=postgresql+asyncpg://couple_space:$(openssl rand -hex 16)@postgres:5432/couple_space|g" backend/.env
    sed -i "s/development/production/g" backend/.env
    sed -i "s/DEBUG=True/DEBUG=False/g" backend/.env
    echo -e "${GREEN}✓ 环境变量配置完成${NC}"
else
    echo -e "${GREEN}✓ 环境变量文件已存在${NC}"
fi

# 启动服务
echo -e "${YELLOW}[7/8] 启动服务...${NC}"
docker compose down 2>/dev/null || true
docker compose up -d --build

echo -e "${YELLOW}等待服务启动...${NC}"
sleep 20
echo -e "${GREEN}✓ 服务启动完成${NC}"

# 健康检查
echo -e "${YELLOW}[8/8] 健康检查...${NC}"
SERVER_IP=$(hostname -I | awk '{print $1}')

if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ 后端服务正常${NC}"
else
    echo -e "${RED}✗ 后端服务未就绪${NC}"
    echo -e "${YELLOW}⚠ 查看日志: docker compose logs${NC}"
fi

if docker compose ps | grep -q "postgres.*Up"; then
    echo -e "${GREEN}✓ PostgreSQL 正常${NC}"
else
    echo -e "${RED}✗ PostgreSQL 未就绪${NC}"
fi

if docker compose ps | grep -q "redis.*Up"; then
    echo -e "${GREEN}✓ Redis 正常${NC}"
else
    echo -e "${RED}✗ Redis 未就绪${NC}"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  部署完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}服务信息:${NC}"
echo "  - 后端 API: http://${SERVER_IP}:8000"
echo "  - API 文档: http://${SERVER_IP}:8000/docs"
echo "  - 项目目录: ${PROJECT_DIR}"
echo ""
echo -e "${YELLOW}常用命令:${NC}"
echo "  - 查看日志: docker compose logs -f"
echo "  - 查看状态: docker compose ps"
echo "  - 重启服务: docker compose restart"
echo ""
