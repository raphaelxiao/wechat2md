# WeChat2MD: 微信公众号文章转 Markdown 工具及 Agent Skill

这是一个完整的解决方案，包含：
1. **API 服务端**：部署在云服务器（推荐腾讯云），用于绕过微信反爬并转换文章。
2. **Agent Skill**：供 AI Agent（如 Antigravity, Claude 等）调用的技能插件。

---

## 第一部分：部署 API 服务端 (Tencent Cloud)

由于微信文章有严格的反爬机制，建议部署在腾讯云服务器上以获得最稳定的解析效果。

### 1. 准备环境
- 确保服务器已安装 Docker 和 Docker Compose。
- 在腾讯云控制台防火墙中开放 **8001** 端口（或其他你自定义的端口）。

### 2. 快速部署
在服务器上创建目录并生成文件：
```bash
mkdir -p /opt/wechat2md && cd /opt/wechat2md

# 使用我们在项目中提供的“硬核”生成脚本（见 deploy_tencent_cloud.md）
# 或者直接 git clone（如果服务器网络通畅）：
git clone https://ghp.ci/https://github.com/raphaelxiao/wechat2md.git .
```

### 3. 配置与启动
```bash
# 生成安全 Token
python3 -c "import secrets; import string; print(''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32)))"

# 写入配置文件
echo "API_TOKEN=你的Token" > .env

# 启动服务
sudo docker compose up -d
```

---

## 第二部分：配置 Agent Skill (wechat-article-fetcher)

部署好服务端后，你可以让你的 Agent “学会”读取微信文章。

### 1. 技能安装 (Step by Step)

1. **进入技能目录**：
   找到 `wechat-article-fetcher/wechat-article-fetcher` 文件夹。

2. **配置环境变量**：
   将 `.env.example` 重命名为 `.env`。
   ```bash
   cp .env.example .env
   ```
   编辑 `.env` 文件，填入你的服务器信息：
   ```ini
   WECHAT2MD_TOKEN=你在第一部分生成的Token
   WECHAT2MD_URL=http://<你的服务器公网IP>:8001/api/v1/wechat2md
   ```

3. **让 Agent 加载技能**：
   将该文件夹提供给 Agent（如在此对话中直接使用）。Agent 会自动识别 `SKILL.md` 并学会如何调用脚本。

### 2. 使用方法

你可以直接对 Agent 说：
> “帮我读取一下这篇文章：https://mp.weixin.qq.com/s/xxxxxxxx”

Agent 会自动：
1. 识别出这是一个微信链接。
2. 调用 `wechat_fetcher.py` 脚本请求你的云端 API。
3. 获取解析后的 Markdown 内容并展示或处理。

---

## 开发与调试

- **本地测试 API**: `uvicorn main:app --reload`
- **查看容器日志**: `sudo docker compose logs -f`
- **手动测试脚本**: `python scripts/wechat_fetcher.py "URL"`

---

## 许可证
MIT
