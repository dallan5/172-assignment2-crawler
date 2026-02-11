# test_fetch_and_extract.py
import re
import sys
import requests
from urllib.parse import urljoin, urldefrag, urlparse
from bs4 import BeautifulSoup
from utils import download
import requests
import cbor
import time

from utils.response import Response
def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    if resp is None:
        return []
    if resp.status != 200:
        return []
    if resp.raw_response is None:
        return []
    
    html = resp.raw_response.content
    if not html:
        return []

    soup = BeautifulSoup(html, "lxml")

    links = []
    for a in soup.find_all("a", href=True):
        href = a.get("href")
        abs_url = urljoin(url, href)
        abs_url, _ = urldefrag(abs_url)
        links.append(abs_url)

    return list()

def extract_links(base_url: str, html: bytes):
    # using beautiful soup to parse and find href:
    # https://stackoverflow.com/questions/5815747/beautifulsoup-getting-href
    soup = BeautifulSoup(html)
    out = set()
    
    for a in soup.find_all("a", href=True):
        u = urljoin(base_url, a["href"])
        u, _ = urldefrag(u)
        out.add(u.rstrip("/"))  # optional normalization
    return list(out)

def is_valid_for_test(url: str) -> bool:
    # keep it simple for CSN test: http(s) only + avoid obvious non-html binaries
    try:
        p = urlparse(url)
        if p.scheme not in {"http", "https"}:
            return False
        return not re.search(
            r"\.(css|js|bmp|gif|jpe?g|ico|png|tiff?|mp3|mp4|wav|avi|mov|mkv|ogg|pdf|"
            r"pptx?|docx?|xlsx?|zip|rar|gz|7z)$",
            p.path.lower()
        )
    except Exception:
        return False
    
def download(url):
    host, port = "https://www.ics.uci.edu/", 80
    resp = requests.get(
        f"http://{host}:{port}/",
        params=[("q", f"{url}")])
    try:
        if resp and resp.content:
            return Response(cbor.loads(resp.content))
    except (EOFError, ValueError) as e:
        pass
    return Response({
        "error": f"Spacetime Response error {resp} with url {url}.",
        "status": resp.status_code,
        "url": url})


def main(url: str):
    resp = download(url)

    base_url = r.url  # final after redirects
    links = extract_next_links(base_url, resp)
    valid = [u for u in links if is_valid_for_test(u)]

    print("base:", base_url)
    print("extracted:", len(links))
    print("valid:", len(valid))
    for u in valid[:50]:
        print(u)


def test_html_parsing():
    from pathlib import Path
    url = "https://www.ics.uci.edu/"
    html = Path("ics.html").read_text(encoding="utf-8")
    #html = resp.raw<+response.content
    print(type(html))

    soup = BeautifulSoup(html, "lxml")

    
    print("hello")
    links = []
    for a in soup.find_all("a", href=True):
        href = a.get("href")
        abs_url = urljoin(url, href)
        abs_url, _ = urldefrag(abs_url)
        links.append(abs_url)
    for x in links:
        print(x)
        #test_html_parsing(x)

if __name__ == "__main__":
    #main(sys.argv[1] if len(sys.argv) > 1 else "https://cnn.com/")

    test_html_parsing()