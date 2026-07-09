import requests
import json
import os
import re
import time
from markdownify import markdownify as html_to_md

URL = "https://support.optisigns.com/api/v2/help_center/en-us/articles.json"
REQUEST_DELAY = 0.3
OUTPUT_DIR = "scrape_result"
PAGE_SIZE = 100

def fetch_articles():
    articles = []
    params = {"page[size]": PAGE_SIZE}
    page_count = 0
    url = URL

    while url:
        page_count += 1
        print(f"Fetching page {page_count}")

        max_retries = 3
        data = None
        for attempt in range(1, max_retries + 1):
            try:
                resp = requests.get(url, params=params if page_count == 1 else None, timeout=30)
                resp.raise_for_status()
                data = resp.json()
                break 

            except requests.exceptions.Timeout:
                print(f"  [!] Timeout (attempt {attempt}/{max_retries}), retrying...")
                time.sleep(2 * attempt)

            except requests.exceptions.HTTPError as e:
                status = e.response.status_code
                if status == 429:
                    wait = int(e.response.headers.get("Retry-After", 5))
                    print(f"  [!] Rate-limited (429), waiting {wait}s...")
                    time.sleep(wait)
                elif status >= 500:
                    print(f"  [!] Server error ({status}), retrying in 3s...")
                    time.sleep(3)
                else:
                    print(f"  [x] HTTP {status} error, not retryable: {url}")
                    raise

            except requests.exceptions.RequestException as e:
                print(f"  [!] Connection error: {e}, retrying...")
                time.sleep(2 * attempt)

        if data is None:
            raise RuntimeError(f"Fetch failed after {max_retries} attempts: {url}")

        articles.extend(data.get("articles", []))
        meta = data.get("meta", {})
        has_more = meta.get("has_more")
        links = data.get("links", {})
        next = links.get("next")

        if next and has_more:
            url = next
        else:
            url = None

        time.sleep(REQUEST_DELAY)

    return articles

def normalize_html(html_body:str):
    if not html_body:
        return ""
    
    markdown = html_to_md(
        html_body,
        heading_style="ATX",
        bullets="*",
        strip=["script", "style"]
    )

    markdown = re.sub(r"\n{3,}", "\n\n", markdown).strip()
    return markdown

def slugify(text:str):
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-{2,}", "-", text).strip()
    return text or "untitled"

def save_articles(article:dict, output_dir:str):
    title = article.get("title", "untitled")
    slug = slugify(title)
    file_path = os.path.join(output_dir, f"{slug}.md")

    body_md = normalize_html(article.get("body", ""))

    content = f"# {title}\n\n" + body_md + "\n"

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    # Use edited_at to track actual content changes instead of general metadata changes
    edited_at = article.get("edited_at", "")
    return file_path, edited_at

def fetch_and_save_articles():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    articles = fetch_articles()

    if len(articles) < 30:
        print("Warning: Unusually low number of articles fetched.")

    scraped_data = []
    for index, article in enumerate(articles, start=1):
        path, edited_at = save_articles(article, OUTPUT_DIR)
        print(f"({index}/{len(articles)}) Saved: {path}")
        if path:
            scraped_data.append({
                "file_path": path,
                "edited_at": edited_at
            })
    return scraped_data

if __name__ == "__main__":
    fetch_and_save_articles()