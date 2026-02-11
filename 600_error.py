import re

LOG_FILE = "Logs/Worker.log"

pattern = re.compile(r"^(.*?) - .*?Downloaded (.*?)\, status <(\d+)>")

def find_600_errors(log_path):
    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            match = pattern.search(line)
            if not match:
                continue

            timestamp, url, status = match.groups()
            status = int(status)

            if 600 <= status < 700:
                print(f"{timestamp} | {status} | {url}")

if __name__ == "__main__":
    find_600_errors(LOG_FILE)
