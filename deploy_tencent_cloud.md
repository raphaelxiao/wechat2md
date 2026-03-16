# 微信公众号文章转 Markdown API - 腾讯云部署指南

本文档将指导你如何在腾讯云服务器（轻量应用服务器或 CVM）上使用 Docker 部署该 API。

## 1. 准备工作

1. **购买服务器**：在腾讯云上购买一台轻量应用服务器（LightHouse）或普通 CVM。对于此应用，1核2G 的配置完全足够。系统推荐选择 **Ubuntu 20.04/22.04 LTS** 或 **Debian 11/12**。
2. **开放端口**：在腾讯云控制台的服务器 防火墙/安全组 设置中，放通 **TCP 8000** 端口，以允许外部访问 API。如果使用反向代理（如 Nginx），则需要放通 80 和 443 端口。

## 2. 登录服务器并安装 Docker

使用 SSH 登录到你的腾讯云服务器：
```bash
ssh root@<你的服务器IP>
```

安装一键部署的 Docker 环境：
```bash
curl -fsSL https://get.docker.com | bash -s docker --mirror Aliyun
```
安装完成后，启动 Docker：
```bash
sudo systemctl start docker
sudo systemctl enable docker
```

安装 Docker Compose 插件（较新版本的 Docker CE 已经自带 `docker compose` 命令，如果没有，可按照官方文档安装，或者使用以下简单命令）：
```bash
sudo apt-get update && sudo apt-get install docker-compose-plugin -y
```

## 3. 部署代码

在服务器上创建一个应用目录并由当前用户管理（推荐）：
```bash
sudo mkdir -p /opt/wechat2md
sudo chown $USER:$USER /opt/wechat2md
cd /opt/wechat2md
```
或者，你也可以选择在用户家目录下部署：`mkdir ~/wechat2md && cd ~/wechat2md`。

然后在服务器上克隆或创建代码：

**选项 A：使用 GitHub 代理（最快）**
```bash
git clone https://ghp.ci/https://github.com/raphaelxiao/wechat2md.git .
```

**选项 B：无网络/备选方案（最可靠 - 直接在服务器生成文件）**
如果 Git 克隆一直失败，请直接在服务器终端**一次性复制并运行**以下命令。它会自动创建所有必要文件：

```bash
cat << 'EOF' > main.py
from fastapi import FastAPI, Depends, HTTPException, Header
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md
import os

app = FastAPI(title="WeChat to Markdown API")
API_TOKEN = os.getenv("API_TOKEN", "default_secret_token")

class ArticleRequest(BaseModel):
    url: str

def verify_token(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer" or token != API_TOKEN:
            raise HTTPException(status_code=403, detail="Invalid token")
    except:
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    return token

@app.post("/api/v1/wechat2md", dependencies=[Depends(verify_token)])
def convert_wechat_to_markdown(request: ArticleRequest):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(request.url, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    soup = BeautifulSoup(response.text, "html.parser")
    title = soup.find("h1", class_="rich_media_title").get_text(strip=True) if soup.find("h1", class_="rich_media_title") else "Untitled"
    content_tag = soup.find("div", id="js_content")
    if not content_tag:
        raise HTTPException(status_code=404, detail="Content not found")
    
    for img in content_tag.find_all("img"):
        if img.has_attr("data-src"): img["src"] = img["data-src"]
    
    markdown_text = md(str(content_tag), heading_style="ATX", strip=['script', 'style'])
    return {"title": title, "markdown_content": f"# {title}\n\n{markdown_text}"}
EOF

cat << 'EOF' > requirements.txt
fastapi
uvicorn[standard]
requests
beautifulsoup4
markdownify
pydantic
EOF

cat << 'EOF' > Dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

cat << 'EOF' > docker-compose.yml
services:
  wechat2md:
    build: .
    container_name: wechat2md_api
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - API_TOKEN=${API_TOKEN:-your_secure_random_token_here}
EOF
```

## 4. 配置与启动

在 `/opt/wechat2md` 目录下，创建一个 `.env` 文件来存储你的安全密钥。

你可以运行以下命令生成一个随机的安全 Token（如果你已经在本地克隆了代码）：
```bash
python3 generate_token.py
```

或者直接手动创建一个强密码并写入 `.env`：
```bash
echo "API_TOKEN=这里替换成你生成的强大的Token" > .env
```
*备注：使用 `.env` 是为了不把 Token 直接写在 docker-compose 文件中。*

确认文件都在目录下后，使用 Docker Compose 构建并启动服务：

```bash
sudo docker compose up -d
```
*备注：如果遇到 `permission denied` 错误，说明需要管理员权限，请务必加 `sudo`。*

*(可选) 如果不想每次都加 sudo，可以运行 `sudo usermod -aG docker $USER` 然后退出并重新登录服务器。*

等待构建和启动完成。你可以通过以下命令查看日志：
```bash
sudo docker compose logs -f
```

## 5. 测试 API

部署成功后，你可以使用本机的终端、Postman 或是你的 Agent 来测试是否成功连通：

```bash
curl -X POST http://<你的服务器IP>:8000/api/v1/wechat2md \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer 这里替换成你自定义的强大的Token" \
  -d '{"url": "https://mp.weixin.qq.com/s/替换成真实的微信文章链接"}'
```

如果返回了 JSON 格式的 Markdown 数据，即表示部署成功！
