#!/bin/bash

# ================================================
# 情侣小空间 APP - 阿里云服务器部署脚本（含 HTTPS）
# 系统: Alibaba Cloud Linux 3 / CentOS 8+
# ================================================

set -e  # 遇到错误立即退出

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目配置
PROJECT_DIR="/opt/couple-space-app"
GITHUB_REPO="https://github.com/jjt256723/couple-space-app.git"
DOMAIN="your-domain.com"  # TODO: 替换为你的域名
SERVER_IP=$(hostname -I | awk '{print $1}')

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  情侣小空间 APP - 自动部署脚本${NC}"
echo -e "${GREEN}  包含 HTTPS + Nginx 反向代理${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# ================================================
# 步骤 1: 更新系统
# ================================================
echo -e "${YELLOW}[1/11] 更新系统...${NC}"
sudo dnf update -y
echo -e "${GREEN}✓ 系统更新完成${NC}"
echo ""

# ================================================
# 步骤 2: 安装基础工具
# ================================================
echo -e "${YELLOW}[2/11] 安装基础工具...${NC}"
sudo dnf install -y git curl vim htop net-tools certbot
echo -e "${GREEN}✓ 基础工具安装完成${NC}"
echo ""

# ================================================
# 步骤 3: 安装 Docker
# ================================================
echo -e "${YELLOW}[3/11] 安装 Docker...${NC}"

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

docker --version
echo ""

# ================================================
# 步骤 4: 安装并配置 Nginx
# ================================================
echo -e "${YELLOW}[4/11] 安装 Nginx...${NC}"

if ! command -v nginx &> /dev/null; then
    sudo dnf install -y nginx
    sudo systemctl start nginx
    sudo systemctl enable nginx

    # 配置 SELinux（如果存在）
    if command -v getenforce &> /dev/null; then
        sudo setsebool -P httpd_can_network_connect 1
    fi

    echo -e "${GREEN}✓ Nginx 安装完成${NC}"
else
    echo -e "${GREEN}✓ Nginx 已安装，跳过${NC}"
fi
echo ""

# ================================================
# 步骤 5: 配置防火墙
# ================================================
echo -e "${YELLOW}[5/11] 配置防火墙...${NC}"

if command -v firewall-cmd &> /dev/null; then
    sudo firewall-cmd --permanent --add-port=80/tcp    # HTTP
    sudo firewall-cmd --permanent --add-port=443/tcp   # HTTPS
    sudo firewall-cmd --permanent --add-port=8000/tcp  # 后端（内部访问）
    sudo firewall-cmd --reload
    echo -e "${GREEN}✓ 防火墙配置完成${NC}"
else
    echo -e "${YELLOW}⚠ 未检测到 firewalld，跳过防火墙配置${NC}"
fi

echo -e "${YELLOW}⚠ 请在阿里云控制台手动配置安全组:${NC}"
echo "   - 开放端口 80（HTTP）"
echo "   - 开放端口 443（HTTPS）"
echo ""
echo -e "${YELLOW}⚠ 如需配置 HTTPS，请先购买域名并解析到服务器 IP: ${SERVER_IP}${NC}"
echo ""

# 询问是否配置 HTTPS
read -p "是否配置 HTTPS？需要已解析的域名 (y/n): " use_https

if [ "$use_https" = "y" ] || [ "$use_https" = "Y" ]; then
    read -p "请输入你的域名 (如: example.com): " input_domain
    DOMAIN=${input_domain}
fi

# ================================================
# 步骤 6: 克隆项目
# ================================================
echo -e "${YELLOW}[6/11] 克隆项目...${NC}"

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
# 步骤 7: 配置环境变量
# ================================================
echo -e "${YELLOW}[7/11] 配置环境变量...${NC}"

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
# 步骤 8: 启动后端服务
# ================================================
echo -e "${YELLOW}[8/11] 启动后端服务...${NC}"

# 停止旧容器（如果有）
docker compose down 2>/dev/null || true

# 构建并启动
docker compose up -d --build

# 等待服务启动
echo -e "${YELLOW}等待服务启动...${NC}"
sleep 15

echo -e "${GREEN}✓ 后端服务启动完成${NC}"
echo ""

# ================================================
# 步骤 9: 配置 Nginx 反向代理
# ================================================
echo -e "${YELLOW}[9/11] 配置 Nginx 反向代理...${NC}"

# 创建 Nginx 配置
sudo tee /etc/nginx/conf.d/couple-space.conf > /dev/null <<EOF
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    server {
        listen 80;
        server_name ${DOMAIN};

        # 健康检查
        location /health {
            proxy_pass http://backend;
            access_log off;
        }

        # API 代理
        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }

        # WebSocket 代理
        location /ws/ {
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade \$http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_connect_timeout 3600s;
            proxy_send_timeout 3600s;
            proxy_read_timeout 3600s;
        }

        # 根路径重定向到 API 文档
        location = / {
            return 301 /docs;
        }

        # FastAPI 文档
        location /docs {
            proxy_pass http://backend;
            proxy_set_header Host \$host;
        }

        location /redoc {
            proxy_pass http://backend;
            proxy_set_header Host \$host;
        }

        location /openapi.json {
            proxy_pass http://backend;
            proxy_set_header Host \$host;
        }
    }
}
EOF

# 测试 Nginx 配置
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx

echo -e "${GREEN}✓ Nginx 配置完成${NC}"
echo ""

# ================================================
# 步骤 10: 配置 HTTPS（Let's Encrypt）
# ================================================
if [ "$use_https" = "y" ] || [ "$use_https" = "Y" ]; then
    echo -e "${YELLOW}[10/11] 配置 HTTPS...${NC}"

    # 获取 SSL 证书
    sudo certbot certonly --nginx -d $DOMAIN --email admin@$DOMAIN --agree-tos --non-interactive

    # 创建 HTTPS 配置
    sudo tee /etc/nginx/conf.d/couple-space-https.conf > /dev/null <<EOF
server {
    listen 443 ssl http2;
    server_name ${DOMAIN};

    ssl_certificate /etc/letsencrypt/live/${DOMAIN}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/${DOMAIN}/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    upstream backend {
        server backend:8000;
    }

    # HSTS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    location /health {
        proxy_pass http://backend;
        access_log off;
    }

    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /ws/ {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_connect_timeout 3600s;
        proxy_send_timeout 3600s;
        proxy_read_timeout 3600s;
    }

    location = / {
        return 301 /docs;
    }

    location /docs {
        proxy_pass http://backend;
        proxy_set_header Host \$host;
    }

    location /redoc {
        proxy_pass http://backend;
        proxy_set_header Host \$host;
    }

    location /openapi.json {
        proxy_pass http://backend;
        proxy_set_header Host \$host;
    }
}

# HTTP 自动跳转 HTTPS
server {
    listen 80;
    server_name ${DOMAIN};
    return 301 https://\$server_name\$request_uri;
}
EOF

    # 测试并重启 Nginx
    sudo nginx -t && sudo systemctl restart nginx

    # 设置自动续期
    echo "0 0 * * * root certbot renew --quiet && nginx -s reload" | sudo tee /etc/cron.d/certbot-renew

    echo -e "${GREEN}✓ HTTPS 配置完成${NC}"
    echo ""
else
    echo -e "${YELLOW}[10/11] 跳过 HTTPS 配置${NC}"
    echo ""
fi

# ================================================
# 步骤 11: 健康检查
# ================================================
echo -e "${YELLOW}[11/11] 健康检查...${NC}"

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

# 检查 Nginx
if sudo systemctl is-active --quiet nginx; then
    echo -e "${GREEN}✓ Nginx 正常${NC}"
else
    echo -e "${RED}✗ Nginx 未就绪${NC}"
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

if [ "$use_https" = "y" ] || [ "$use_https" = "Y" ]; then
    echo "  - 后端 API: https://${DOMAIN}/api/v1"
    echo "  - API 文档: https://${DOMAIN}/docs"
else
    echo "  - 后端 API: http://${SERVER_IP}/api/v1"
    echo "  - API 文档: http://${SERVER_IP}/docs"
fi

echo "  - 服务器 IP: ${SERVER_IP}"
echo "  - 项目目录: ${PROJECT_DIR}"
echo ""

echo -e "${YELLOW}常用命令:${NC}"
echo "  - 查看日志:    docker compose logs -f"
echo "  - 查看状态:    docker compose ps"
echo "  - 停止服务:    docker compose down"
echo "  - 重启服务:    docker compose restart"
echo "  - 进入容器:    docker compose exec backend bash"
echo "  - Nginx 日志:  sudo tail -f /var/log/nginx/access.log"
echo "  - Nginx 配置:  sudo vim /etc/nginx/conf.d/couple-space.conf"
echo ""

echo -e "${YELLOW}数据库迁移（首次运行）:${NC}"
echo "  docker compose exec backend alembic upgrade head"
echo ""

echo -e "${YELLOW}创建测试用户:${NC}"
if [ "$use_https" = "y" ] || [ "$use_https" = "Y" ]; then
    echo "  curl -X POST https://${DOMAIN}/api/v1/auth/register \\"
else
    echo "  curl -X POST http://${SERVER_IP}/api/v1/auth/register \\"
fi
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"username\":\"test\",\"email\":\"test@example.com\",\"nickname\":\"测试\",\"password\":\"123456\"}'"
echo ""
