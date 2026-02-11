import re
from urllib.parse import urljoin, urldefrag, urlparse
from bs4 import BeautifulSoup

def scraper(url, resp):
    """
    Orchestrates the extraction and validation of links.
    Logs valid URLs to valid_urls.txt as they are confirmed.
    """
    links = extract_next_links(url, resp)
    valid_links = []
    
    # Open file in append mode ('a') so we don't overwrite previous progress
    with open("valid_urls.txt", "a", encoding="utf-8") as f:
        for link in links:
            if is_valid(link):
                valid_links.append(link)
                # Write to file immediately
                f.write(link + "\n")
                
    return valid_links

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

    # 1. Defensive Checks: Ensure we have a valid, successful response
    if not resp or resp.status != 200 or not resp.raw_response:
        return []

    # 2. Content-Type Check: Don't parse if it's not HTML (e.g., a sneaky PDF that missed the status check)
    content_type = resp.raw_response.headers.get("Content-Type", "").lower()
    if "text/html" not in content_type:
        return []

    # 3. HTML Extraction
    html = resp.raw_response.content
    if not html:
        return []

    # 4. Parsing Setup
    # Use resp.url (the final URL after redirects) as the base for relative links
    base_url = resp.url if resp.url else url
    soup = BeautifulSoup(html, "lxml")
    
    # Using a set to ensure uniqueness as per assignment rules
    unique_links = set()

    # 5. Extraction Loop
    for a in soup.find_all("a", href=True):
        href = a.get("href").strip()
        
        # Skip empty hrefs or non-web protocols
        if not href or any(href.startswith(p) for p in ["#", "mailto:", "javascript:", "tel:"]):
            continue

        # Convert relative to absolute (e.g., "about/" -> "https://ics.uci.edu/about/")
        abs_url = urljoin(base_url, href)
        
        # Defragment: Remove everything after the '#' (Requirement: unique pages)
        clean_url, _ = urldefrag(abs_url)
        
        unique_links.add(clean_url)

    return list(unique_links)

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
    try:
        # 1. Basic Type Check
        if not url or not isinstance(url, str):
            return False
            
        parsed = urlparse(url)
        
        # 2. Protocol Check
        if parsed.scheme not in {"http", "https"}:
            return False

        # 3. Domain Validation
        host = (parsed.hostname or "").lower()
        if not host:
            return False

        allowed = ["ics.uci.edu", "cs.uci.edu", "informatics.uci.edu", "stat.uci.edu"]
        if not any(host == d or host.endswith("." + d) for d in allowed):
            return False

        # 4. Path and Query assignments (Done before checks to avoid NameErrors)
        path = parsed.path.lower()
        query = parsed.query.lower()

        # 5. Trap and Low-Information Value Detection
        if query:
            # Block the 'tribe' calendar traps
            if "tribe" in query:
                return False
            # Block the news filter archives (Low Info Value per grading criteria)
            if "filter[" in query or "affiliation_posts" in query:
                return False
            # Block combinatorial explosions (too many parameters)
            if query.count('&') > 2:
                return False

        # 6. Repetitive Directory Trap (e.g., /news/news/news/)
        segments = [s for s in path.split("/") if s]
        if len(segments) != len(set(segments)):
            return False

        # 7. File Extension Filtering
        if ILLEGAL_EXTENSIONS.match(path):
            return False

        return True

    except Exception as e:
        # For debugging, you can uncomment the next line:
        # print(f"Error validating {url}: {e}")
        return False

"""
def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]
"""
"""
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

        host = (p.hostname or "").lower()
        if host.startswith("www."):
            host = host[4:]

        if host != "ics.uci.edu" and not host.endswith(".ics.uci.edu"):
            return False

        # spec #1: filter non-web pages by extension
        path = (p.path or "").lower()
        if ILLEGAL_EXTENSIONS.match(path):
            return False

        return True

    except Exception:
        return False
"""

