import requests
import time
import random

url = "https://site.com/vote"
headers = {"User-Agent": "Mozilla/5.0"}

for i in range(1000):
    # Her seferinde farklı proxy kullan
    proxy = {"http": f"http://{random.choice(proxy_list)}"}
    data = {"city": "istanbul"}  # istediğin şehir
    r = requests.post(url, data=data, headers=headers, proxies=proxy)
    print(i, r.status_code)
    time.sleep(1)  