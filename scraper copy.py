import re
import hashlib
from pathlib import Path
from urllib.parse import urlparse, urljoin, urldefrag
from bs4 import BeautifulSoup

PAGES_DIR = Path("Pages")
PAGES_DIR.mkdir(exist_ok=True)

def save_page(url: str, content: bytes):
    h = hashlib.sha1(url.encode("utf-8")).hexdigest()[:16]
    (PAGES_DIR / f"{h}.html").write_bytes(content)
    (PAGES_DIR / f"{h}.url").write_text(url + "\n", encoding="utf-8")
    
def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    if resp is None or resp.status != 200 or resp.raw_response is None:
        return []

    ctype = resp.raw_response.headers.get("Content-Type", "").lower()
    if "text/html" not in ctype:
        return []

    html = resp.raw_response.content
    if not html:
        return []

    # save page for offline testing
    base_url = resp.raw_response.url or url
    save_page(base_url, html)

    soup = BeautifulSoup(html, "lxml")

    links = []
    for a in soup.find_all("a", href=True):
        href = a.get("href")
        abs_url = urljoin(base_url, href)
        abs_url, _ = urldefrag(abs_url)
        links.append(abs_url)

    return links

ALLOWED = ("ics.uci.edu", "cs.uci.edu", "informatics.uci.edu", "stat.uci.edu")

def is_valid(url):
    try:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            return False

        host = (parsed.hostname or "").lower()
        if not any(host == d or host.endswith("." + d) for d in ALLOWED):
            return False

        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$",
            parsed.path.lower()
        )
    except Exception:
        return False
