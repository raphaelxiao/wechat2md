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
systemctl start docker
systemctl enable docker
```

安装 Docker Compose 插件（较新版本的 Docker CE 已经自带 `docker compose` 命令，如果没有，可按照官方文档安装，或者使用以下简单命令）：
```bash
apt-get update && apt-get install docker-compose-plugin -y
```

## 3. 部署代码

在服务器上创建一个应用目录并由当前用户管理（推荐）：
```bash
sudo mkdir -p /opt/wechat2md
sudo chown $USER:$USER /opt/wechat2md
cd /opt/wechat2md
```
或者，你也可以选择在用户家目录下部署：`mkdir ~/wechat2md && cd ~/wechat2md`。

然后在服务器上克隆代码：

**推荐：使用最稳定的代理（通常无需登录）**
```bash
git clone https://ghp.ci/https://github.com/raphaelxiao/wechat2md.git .
```

**备选：如果上方失效，尝试此地址**
```bash
git clone https://mirror.ghproxy.com/https://github.com/raphaelxiao/wechat2md.git .
```

*(注意：如果提示输入 Username，说明该代理当前被墙或连接质量差，被 Git 误认为需要认证。请尝试更换备选地址，或检查链接拼写是否完全一致。)*

## 4. 配置与启动

在 `/opt/wechat2md` 目录下，创建一个 `.env` 文件来存储你的安全密钥（可选，也可以直接修改 `docker-compose.yml`）。
```bash
echo "API_TOKEN=这里替换成你自定义的强大的Token" > .env
```
*备注：使用 `.env` 是为了不把 Token 直接写在 docker-compose 文件中。*

确认文件都在目录下后，使用 Docker Compose 构建并启动服务：

```bash
docker compose up -d
```
或者如果是老版本：
```bash
docker-compose up -d
```

等待构建和启动完成。你可以通过以下命令查看日志：
```bash
docker compose logs -f
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
