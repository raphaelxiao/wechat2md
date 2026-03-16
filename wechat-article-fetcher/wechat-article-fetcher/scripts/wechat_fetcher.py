#!/usr/bin/env python3
"""
Fetch WeChat article content and convert to Markdown.

Usage:
    python wechat_fetcher.py <wechat_article_url>
    
Environment Variables:
    WECHAT2MD_TOKEN - Bearer token for API authentication
    WECHAT2MD_URL   - API endpoint URL (default: http://[IP_ADDRESS]/api/v1/wechat2md)
"""

import os
import sys
import json
import urllib.request
import urllib.error
from pathlib import Path


def load_env_file(env_path: Path) -> dict:
    """Load environment variables from .env file."""
    env_vars = {}
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    return env_vars


def fetch_wechat_article(url: str, token: str, api_url: str) -> dict:
    """Fetch WeChat article content via API."""
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    
    data = json.dumps({'url': url}).encode('utf-8')
    
    req = urllib.request.Request(
        api_url,
        data=data,
        headers=headers,
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        raise Exception(f"HTTP Error {e.code}: {error_body}")
    except Exception as e:
        raise Exception(f"Request failed: {e}")


def main():
    # Load .env from skill directory
    skill_dir = Path(__file__).parent.parent
    env_path = skill_dir / '.env'
    env_vars = load_env_file(env_path)
    
    # Get configuration
    token = env_vars.get('WECHAT2MD_TOKEN') or os.environ.get('WECHAT2MD_TOKEN')
    api_url = env_vars.get('WECHAT2MD_URL') or os.environ.get(
        'WECHAT2MD_URL', 'http://[IP_ADDRESS]/api/v1/wechat2md'
    )
    
    if not token or token == 'your_token_here':
        print("Error: WECHAT2MD_TOKEN not configured.", file=sys.stderr)
        print("Please set it in .env file or environment variable.", file=sys.stderr)
        sys.exit(1)
    
    if len(sys.argv) < 2:
        print("Usage: python wechat_fetcher.py <wechat_article_url>", file=sys.stderr)
        sys.exit(1)
    
    article_url = sys.argv[1]
    
    # Validate URL
    if not article_url.startswith('https://mp.weixin.qq.com/s/'):
        print(f"Warning: URL doesn't look like a standard WeChat article URL.", file=sys.stderr)
        print(f"Expected format: https://mp.weixin.qq.com/s/...", file=sys.stderr)
    
    try:
        result = fetch_wechat_article(article_url, token, api_url)
        
        # Output the markdown content
        if 'markdown_content' in result:
            print(result['markdown_content'])
        elif 'content' in result:
            print(result['content'])
        elif 'markdown' in result:
            print(result['markdown'])
        elif 'data' in result:
            print(result['data'])
        else:
            print(json.dumps(result, ensure_ascii=False, indent=2))
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
