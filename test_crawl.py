import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urldefrag

LOG_FILE = "links.log"

def crawl(url, visited, max_iters, session):
    if len(visited) >= max_iters:
        return

    if url in visited:
        return

    try:
        r = session.get(url, timeout=3)
        ct = (r.headers.get("Content-Type") or "").lower()
        if "text/html" not in ct:
            return
    except Exception:
        return

    visited.add(url)

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(url + "\n")

    soup = BeautifulSoup(r.text, "html.parser")

    time.sleep(1)

    for a in soup.find_all("a", href=True):
        href = a.get("href")
        abs_url = urljoin(url, href)
        abs_url, _ = urldefrag(abs_url)

        if len(visited) >= max_iters:
            return

        crawl(abs_url, visited, max_iters, session)


def run():
    start_url = "https://www.ics.uci.edu/"
    visited = set()
    session = requests.Session()
    crawl(start_url, visited, max_iters=100, session=session)


if __name__ == "__main__":
    run()
