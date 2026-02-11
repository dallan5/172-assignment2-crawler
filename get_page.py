import requests

url = "https://www.ics.uci.edu"
r = requests.get(url)
with open("ics.html","w",encoding=r.encoding) as f:
    f.write(r.text)
