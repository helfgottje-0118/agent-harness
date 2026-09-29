"""Web tools: fetch a URL as text, and web search (best-effort, no API key)."""
from __future__ import annotations

import html as _html
import re
import urllib.parse
from html.parser import HTMLParser

import requests

_HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) agent-harness/0.1"}


class _TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self._parts: list[str] = []
        self._skip = 0  # depth inside script/style/noscript

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript"):
            self._skip += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript") and self._skip:
            self._skip -= 1

    def handle_data(self, data):
        if not self._skip:
            text = data.strip()
            if text:
                self._parts.append(text)

    def text(self) -> str:
        raw = " ".join(self._parts)
        raw = _html.unescape(raw)
        return re.sub(r"\s+", " ", raw).strip()


def web_fetch(url: str, max_chars: int = 15000) -> str:
    if not url.startswith(("http://", "https://")):
        return "Error: URL must start with http:// or https://"
    try:
        r = requests.get(url, headers=_HEADERS, timeout=20)
        r.raise_for_status()
    except requests.RequestException as e:
        return f"Error fetching {url}: {e}"
    ctype = r.headers.get("Content-Type", "")
    if "html" not in ctype and "text" not in ctype:
        return f"Error: unsupported content type '{ctype}'."
    parser = _TextExtractor()
    try:
        parser.feed(r.text)
    except Exception:
        pass
    text = parser.text()
    if len(text) > max_chars:
        text = text[:max_chars] + f"\n... [truncated at {max_chars} chars]"
    return text or "(no readable text found)"


def web_search(query: str, num_results: int = 5) -> str:
    """Best-effort web search via DuckDuckGo's HTML endpoint (no key needed)."""
    try:
        r = requests.get(
            "https://html.duckduckgo.com/html/",
            params={"q": query},
            headers=_HEADERS,
            timeout=20,
        )
        r.raise_for_status()
    except requests.RequestException as e:
        return f"Error searching: {e}"
    results = []
    # DDG html results: <a class="result__a" href="...">title</a> ... <a class="result__snippet">
    pattern = re.compile(
        r'<a[^>]*class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>.*?<a[^>]*class="result__snippet"[^>]*>(.*?)</a>',
        re.DOTALL,
    )
    for href, title, snippet in pattern.findall(r.text):
        if href.startswith("//"):
            href = "https:" + href
        elif href.startswith("/"):
            continue
        # unwrap DDG redirect links
        if "duckduckgo.com/l/" in href:
            q = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
            href = q.get("uddg", [href])[0]
        clean = lambda s: _html.unescape(re.sub(r"<[^>]+>", "", s)).strip()
        results.append((clean(title), href, clean(snippet)))
        if len(results) >= num_results:
            break
    if not results:
        return "No results found (search backend may be blocking automated queries)."
    lines = []
    for i, (title, href, snippet) in enumerate(results, 1):
        lines.append(f"{i}. {title}\n   {href}\n   {snippet}")
    return "\n\n".join(lines)
