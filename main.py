from fastapi import FastAPI, Depends, HTTPException, Header
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md
import os

app = FastAPI(title="WeChat to Markdown API")

# Retrieve the token from environment variables or use a default one for local testing
API_TOKEN = os.getenv("API_TOKEN", "default_secret_token")

class ArticleRequest(BaseModel):
    url: str

def verify_token(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
        if token != API_TOKEN:
            raise HTTPException(status_code=403, detail="Invalid token")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    return token

@app.post("/api/v1/wechat2md", dependencies=[Depends(verify_token)])
def convert_wechat_to_markdown(request: ArticleRequest):
    url = request.url
    if not url.startswith("http"):
        raise HTTPException(status_code=400, detail="Invalid URL format")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch the article: {str(e)}")

    html_content = response.text
    soup = BeautifulSoup(html_content, "html.parser")

    # Extract title
    title_tag = soup.find("h1", class_="rich_media_title")
    title = title_tag.get_text(strip=True) if title_tag else "Untitled"

    # Extract content body
    content_tag = soup.find("div", id="js_content")
    if not content_tag:
        raise HTTPException(status_code=404, detail="Article content not found (could not find js_content)")

    # WeChat uses data-src for lazy loading. We need to replace them with standard src.
    for img in content_tag.find_all("img"):
        if img.has_attr("data-src"):
            img["src"] = img["data-src"]

    # Convert the extracted HTML to Markdown
    # we convert just the inner HTML of the js_content div
    markdown_text = md(str(content_tag), heading_style="ATX", strip=['script', 'style'])

    # Add the title as an H1 at the top
    final_markdown = f"# {title}\n\n{markdown_text}"

    return {
        "title": title,
        "markdown_content": final_markdown.strip()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
