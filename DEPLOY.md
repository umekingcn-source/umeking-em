# 📧 AI Email Marketing System 部署指南

## 🚀 快速部署到 Streamlit Cloud

### 步骤 1：准备 Git 仓库

1. 在 GitHub 创建一个新的私有仓库
2. 初始化本地 Git 仓库并推送代码：

```bash
cd "D:\20260130-Automated Email Marketing System"
git init
git add .
git commit -m "Initial commit - AI Email Marketing System"
git branch -M main
git remote add origin https://github.com/你的用户名/你的仓库名.git
git push -u origin main
```

### 步骤 2：部署到 Streamlit Cloud

1. 访问 [Streamlit Cloud](https://streamlit.io/cloud)
2. 使用 GitHub 账号登录
3. 点击 "New app"
4. 选择你的仓库和分支 (main)
5. 主文件路径填写：`app.py`
6. 点击 "Deploy"

### 步骤 3：配置 Secrets

在 Streamlit Cloud 的应用设置中，添加以下 secrets：

```toml
# Gemini API 密钥
GEMINI_API_KEY = "你的Gemini API密钥"

# 邮件发送配置（可选，如果在应用中直接输入则不需要）
SMTP_SERVER = "smtp.example.com"
SMTP_PORT = 587
EMAIL_ADDRESS = "your-email@example.com"
EMAIL_PASSWORD = "your-email-password"

# IMAP 配置（用于退信监控）
IMAP_SERVER = "imap.example.com"
IMAP_PORT = 993
```

---

## 🖥️ 本地部署

### 方式 1：直接运行

```bash
# 安装依赖
pip install -r requirements.txt

# 运行应用
streamlit run app.py
```

### 方式 2：使用 Docker

创建 `Dockerfile`：

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

构建并运行：

```bash
docker build -t email-marketing-system .
docker run -p 8501:8501 email-marketing-system
```

---

## ☁️ 部署到云服务器

### 使用 Docker Compose

创建 `docker-compose.yml`：

```yaml
version: '3.8'

services:
  email-marketing:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./send_history:/app/send_history
    environment:
      - STREAMLIT_SERVER_PORT=8501
      - STREAMLIT_SERVER_ADDRESS=0.0.0.0
    restart: unless-stopped
```

运行：

```bash
docker-compose up -d
```

### 使用 Nginx 反向代理（生产环境推荐）

Nginx 配置示例：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
}
```

---

## 🔐 安全注意事项

1. **永远不要**将 `.streamlit/secrets.toml` 提交到 Git
2. 使用环境变量或 Streamlit secrets 管理敏感信息
3. 定期更新依赖包以修复安全漏洞
4. 建议使用 HTTPS（可通过 Cloudflare 或 Let's Encrypt 配置）

---

## 📋 文件结构

```
📦 AI Email Marketing System
├── 📄 app.py                    # 主应用文件
├── 📄 requirements.txt          # Python 依赖
├── 📄 DEPLOY.md                 # 部署指南（本文件）
├── 📁 .streamlit/
│   ├── 📄 config.toml          # Streamlit 配置
│   └── 📄 secrets.toml.example # Secrets 模板
├── 📁 send_history/            # 发送历史记录
└── 📄 .gitignore               # Git 忽略文件
```

---

## ❓ 常见问题

### Q: 部署后发送历史记录会丢失吗？

A: 在 Streamlit Cloud 上，文件系统是临时的，重启后数据会丢失。建议：
- 使用外部数据库（如 Supabase、MongoDB Atlas）
- 或定期导出数据

### Q: 如何自定义端口？

A: 修改 `.streamlit/config.toml` 中的 `port` 值，或使用命令行参数：
```bash
streamlit run app.py --server.port 8080
```

### Q: 邮件发送失败怎么办？

A: 检查：
1. SMTP 服务器地址和端口是否正确
2. 是否开启了"允许不太安全的应用"或使用应用专用密码
3. 网络是否能访问 SMTP 服务器

---

## 📞 技术支持

如有问题，请联系开发团队或查看项目文档。

