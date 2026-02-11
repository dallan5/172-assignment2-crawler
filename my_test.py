import re
import sys
import requests
from urllib.parse import urljoin, urldefrag, urlparse
from bs4 import BeautifulSoup
import requests
import cbor
import time
from pathlib import Path

# NOTE: Since this is a standalone test, I am using a local definition for Response
# if you don't have the utils folder locally.
from utils.response import Response

def get_valid_links_from_url(url):
    """
    Downloads the page at 'url', parses its HTML, 
    and returns a set of unique, valid absolute URLs.
    """
    try:
        # 1. DOWNLOAD: Hit the real server
        headers = {"User-Agent": "UCI-CS121-Crawler-Student-Project"}
        resp = requests.get(url, headers=headers, timeout=5)
        
        if resp.status_code != 200:
            print(f"Failed to fetch {url}: Status {resp.status_code}")
            return set()

        # 2. PARSE: Turn bytes into a searchable soup object
        soup = BeautifulSoup(resp.content, "lxml")
        valid_links = set()

        # 3. EXTRACT, NORMALIZE, AND LOG
        # Open the file in 'append' mode to record valid URLs
        with open("valid_urls.txt", "a", encoding="utf-8") as f:
            for a in soup.find_all("a", href=True):
                href = a.get("href")
                
                # Normalize
                abs_url = urljoin(url, href)
                defragmented_url, _ = urldefrag(abs_url)
                
                # 4. VALIDATE & RECORD
                if is_valid(defragmented_url):
                    if defragmented_url not in valid_links:
                        valid_links.add(defragmented_url)
                        # Write to the text file immediately
                        f.write(defragmented_url + "\n")
                
        return valid_links

    except Exception as e:
        print(f"Error crawling {url}: {e}")
        return set()

# --- is_valid function logic preserved exactly as requested ---
BAD_EXTENSIONS = re.compile(
    r".*\.(css|js|bmp|gif|jpe?g|ico|png|tiff?|svg|webp|"
    r"mid|mp2|mp3|mp4|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|webm|"
    r"pdf|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names|data|dat|"
    r"exe|bz2|tar|msi|bin|7z|psd|dmg|iso|epub|dll|cnf|tgz|sha1|"
    r"thmx|mso|arff|rtf|jar|csv|rm|smil|wmv|swf|wma|zip|rar|gz|war)$",
    re.IGNORECASE
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

        # 4. Path and Query assignments
        path = parsed.path.lower()
        query = parsed.query.lower()

        # 5. Trap and Low-Information Value Detection
        if query:
            if "tribe" in query:
                return False
            if "filter[" in query or "affiliation_posts" in query:
                return False
            if query.count('&') > 2:
                return False

        # 6. Repetitive Directory Trap
        segments = [s for s in path.split("/") if s]
        if len(segments) != len(set(segments)):
            return False

        # 7. File Extension Filtering
        if BAD_EXTENSIONS.match(path):
            return False

        return True

    except Exception:
        return False

if __name__ == "__main__":
    # 1. Define your seeds based on your config file
    seeds = [
        "https://www.ics.uci.edu",
        "https://www.cs.uci.edu",
        "https://www.informatics.uci.edu",
        "https://www.stat.uci.edu"
    ]
    
    print(f"Starting crawl for {len(seeds)} seeds...")
    
    # 2. Loop through each seed to initialize the crawl
    for target in seeds:
        print(f"\n--- Processing Seed: {target} ---")
        
        try:
            # Fetch the page content
            headers = {"User-Agent": "IR W26 46384500"}
            resp = requests.get(target, timeout=5, headers=headers)
            
            if resp.status_code != 200:
                print(f"Failed to reach seed {target}: {resp.status_code}")
                continue
                
            soup = BeautifulSoup(resp.content, "lxml")
            
            # Extract and Filter
            all_discovered_urls = set()
            for a in soup.find_all("a", href=True):
                abs_url = urljoin(target, a.get("href"))
                clean_url, _ = urldefrag(abs_url)
                all_discovered_urls.add(clean_url)

            # 3. Print Results and Write to File
            # Use 'a' to ensure we keep results from all seeds in one file
            with open("valid_urls.txt", "a", encoding="utf-8") as f:
                valid_count = 0
                for link in sorted(all_discovered_urls):
                    if is_valid(link):
                        f.write(link + "\n")
                        valid_count += 1
                
                print(f"Seed {target} complete. Found {valid_count} valid links.")

        except Exception as e:
            print(f"Error processing {target}: {e}")

    print("\nInitialization finished. Check 'valid_urls.txt' for all discovered URLs.")