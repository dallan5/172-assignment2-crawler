import re
import time
import json
import requests
from bs4 import BeautifulSoup
from collections import Counter
from urllib.parse import urlparse

# --- CONFIGURATION ---
LOG_FILE_PATH = "./Logs/Worker.log"
CHECKPOINT_FILE = "crawler_checkpoint.json"
STOPWORDS_FILE = "stopwords.txt"  # Assumes you have the assignment's stopword list
POLITENESS_DELAY = 1.2  # Seconds between requests

# Global data structures
word_frequencies = Counter()
longest_page_url = ""
max_word_count = 0
processed_count = 0

def tokenize_and_count(html_text):
    """Parses visible HTML, tokenizes, and returns a list of words."""
    if not html_text:
        return []
    
    soup = BeautifulSoup(html_text, "lxml")
    
    # Target content-heavy tags to avoid script/style noise
    content_tags = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 
                                  'pre', 'li', 'td', 'th', 'article', 'span', 'div'])
    
    raw_text = " ".join([tag.get_text(separator=' ', strip=True) for tag in content_tags])
    
    # Tokenize: alphanumeric only, lowercase. 
    # This automatically strips special characters.
    tokens = re.findall(r'[a-zA-Z0-9]+', raw_text.lower())
    return tokens

def get_html_response(url):
    """Fetches the HTML content with a custom User-Agent."""
    try:
        headers = {"User-Agent": "IR W26 46384500"} # Using your ID from config
        resp = requests.get(url, headers=headers, timeout=5)
        if resp.status_code == 200:
            # Check if it's actually HTML
            if "text/html" in resp.headers.get("Content-Type", ""):
                return resp.text
        return None
    except Exception:
        return None

def save_checkpoint():
    """Saves current progress to a JSON file."""
    data = {
        "max_word_count": max_word_count,
        "longest_page_url": longest_page_url,
        "processed_count": processed_count,
        "word_frequencies": dict(word_frequencies)
    }
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump(data, f)
    print(f"\n[CHECKPOINT] Saved progress at {processed_count} URLs.")

def process_logs():
    global max_word_count, longest_page_url, processed_count, word_frequencies
    
    # 1. Load Stopwords (optional but recommended for Question #3)
    # You can also filter these at the very end when generating the report.
    
    # 2. Extract URLs from log
    url_pattern = re.compile(r'https?://[^\s,<>]+')
    with open(LOG_FILE_PATH, 'r') as f:
        log_lines = f.readlines()

    total_urls = len(log_lines)
    print(f"Starting processing of {total_urls} URLs...")

    for i, line in enumerate(log_lines):
        match = url_pattern.search(line)
        if not match:
            continue
        
        url = match.group()
        
        # 3. Politeness Delay
        time.sleep(POLITENESS_DELAY)
        
        # 4. Fetch and Process
        html = get_html_response(url)
        if html:
            words = tokenize_and_count(html)
            word_len = len(words)
            
            # Update Frequencies
            word_frequencies.update(words)
            
            # Track Longest Page
            if word_len > max_word_count:
                max_word_count = word_len
                longest_page_url = url
        
        processed_count += 1
        
        # 5. Status Update & Checkpoint every 100 URLs
        if processed_count % 10 == 0:
            print(f"Progress: {processed_count}/{total_urls} | Longest so far: {max_word_count} words", end="\r")
        
        if processed_count % 100 == 0:
            save_checkpoint()

    # 6. Final Report Generation
    print("\n\n" + "="*40)
    print("FINAL CRAWL REPORT DATA")
    print("="*40)
    print(f"Unique Pages Found: {total_urls}") # Based on your log lines
    print(f"Longest Page URL: {longest_page_url}")
    print(f"Max Word Count: {max_word_count}")
    print("="*40)
    
    # Export word counts for final filtering
    save_checkpoint()
    print("All data saved to crawler_checkpoint.json")

if __name__ == "__main__":
    try:
        process_logs()
    except KeyboardInterrupt:
        print("\nProcess interrupted by user. Saving current progress...")
        save_checkpoint()