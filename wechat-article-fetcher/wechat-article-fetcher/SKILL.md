---
name: wechat-article-fetcher
description: 微信公众号文章解析技能 (OpenClaw)。通过调运腾讯云解析代理绕过微信反爬，将文章 URL 转换为 Markdown 高质量文本。适用于内容抓取、信息总结及知识库沉淀。
---

# WeChat Article Fetcher (OpenClaw Skill)

通过调运远程的云端解析服务，稳定获取微信公众号文章内容并转换为 Markdown。

## 前置条件

1. **部署云端代理**：确保你已按照项目根目录的 [README.md](../../README.md) 在腾讯云完成 Cloud Proxy 的部署。
2. **配置环境**：
   - 将技能目录下的 `.env.example` 复制并重命名为 `.env`。
   - 在 `.env` 中设置你的 API Token 和服务器地址：
     ```ini
     WECHAT2MD_TOKEN=你在服务端设置的Token
     WECHAT2MD_URL=http://<服务器IP>:8001/api/v1/wechat2md
     ```

## Usage

### Direct Script Execution

```bash
python scripts/wechat_fetcher.py "https://mp.weixin.qq.com/s/xxxxx"
```

### From SKILL.md Context

When processing a WeChat article URL for the user:

1. Extract the WeChat article URL (format: `https://mp.weixin.qq.com/s/...`)
2. Run the fetcher script with the URL
3. Return the markdown content to the user

Example workflow:
```python
import subprocess
result = subprocess.run(
    ['python', 'scripts/wechat_fetcher.py', url],
    capture_output=True,
    text=True,
    cwd=skill_directory
)
markdown_content = result.stdout
```

## API Details

- **Endpoint**: `http://[IP_ADDRESS]/api/v1/wechat2md`
- **Method**: POST
- **Headers**: 
  - `Content-Type: application/json`
  - `Authorization: Bearer <TOKEN>`
- **Body**: `{"url": "https://mp.weixin.qq.com/s/..."}`

The cloud service handles WeChat's anti-scraping measures, allowing reliable content extraction.
