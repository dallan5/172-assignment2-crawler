import re
from urllib.parse import urljoin, urldefrag, urlparse
from bs4 import BeautifulSoup

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

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

    # check header content type and make sure text/html in there
    content_type = resp.raw_response.headers.get("Content-Type", "").lower()
    if "text/html" not in content_type:
        return []

    # make sure we have content in our raw response
    html = resp.raw_response.content
    if not html:
        return []

    # using beautiful soup to parse and find href:
    # https://stackoverflow.com/questions/5815747/beautifulsoup-getting-href
    base_url = resp.url or url
    soup = BeautifulSoup(html, "lxml")

    links = []
    for a in soup.find_all("a", href=True):
        href = a.get("href")
        #get rid of all href starting with
        if not href:
            continue

        href = href.strip()
        

        if href.startswith(("#", "mailto:", "javascript:", "tel:")):
            continue

        abs_url = urljoin(base_url, href)
        abs_url, _ = urldefrag(abs_url)
        links.append(abs_url)

    return links


ILLEGAL_EXTENSIONS = re.compile(
    r".*\.(css|js|bmp|gif|jpe?g|ico|png|tiff?|svg|webp|"
    r"mid|mp2|mp3|mp4|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|webm|"
    r"pdf|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|"
    r"zip|rar|gz|tgz|bz2|7z|tar|"
    r"exe|msi|bin|dmg|iso|dll|"
    r"csv|tsv|arff|rtf|jar|war)$",
    re.IGNORECASE,
)

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        if not url or not isinstance(url, str):
            return False

        p = urlparse(url)

        if p.scheme not in ("http", "https"):
            return False
        
        if p.query:
            return False

        host = (p.hostname or "").lower().rstrip(".")
        if host.startswith("www."):
            host = host[4:]

        ALLOWED_HOSTS = {
            "ics.uci.edu",
            "cs.uci.edu",
            "informatics.uci.edu",
            "stat.uci.edu",
        }

        if host not in ALLOWED_HOSTS:
            return False

        # spec #1: filter non-web pages by extension
        path = (p.path or "").lower()
        if ILLEGAL_EXTENSIONS.match(path):
            return False

        return True

    except Exception:
        return False

