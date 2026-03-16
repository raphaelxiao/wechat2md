---
name: wechat-article-fetcher
description: Fetch WeChat public account articles and convert to Markdown using a cloud API. Use when the user wants to extract content from WeChat articles (mp.weixin.qq.com URLs) for reading, archiving, or processing. The skill handles anti-scraping by calling a cloud-based conversion service.
---

# WeChat Article Fetcher

Fetch WeChat public account articles and convert them to Markdown format.

## Prerequisites

1. Copy `.env.example` to `.env` in the skill directory
2. Set your API token in `.env`:
   ```
   WECHAT2MD_TOKEN=your_actual_token_here
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
