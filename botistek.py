import requests
import time
import random
import threading
from bs4 import BeautifulSoup
from queue import Queue

# OYLAMA SİTESİ
URL = "https://okul-sitesi.com/oy-ver"
SEHIR = "istanbul"

# PROXY LISTESI (kendi proxy dosyandan okursun)
def proxy_yukle(dosya="proxies.txt"):
    with open(dosya, "r") as f:
        return [line.strip() for line in f if line.strip()]

# USER-AGENT LISTESI
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36"
]

# HER THREAD ICIN AYRI OTURUM
def oy_ver(proxy, sayac):
    try:
        session = requests.Session()
        session.headers.update({
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "tr-TR,tr;q=0.9,en;q=0.8",
            "Referer": URL,
            "Origin": URL.replace("/oy-ver", "")
        })

        # Ana sayfayi ziyaret et (insan gibi)
        session.get(URL.replace("/oy-ver", ""), timeout=10)
        time.sleep(random.uniform(0.5, 2.0))

        # Oylama sayfasini ac
        r = session.get(URL, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        # CSRF token varsa al
        token = None
        token_input = soup.find("input", {"name": "csrf_token"}) or soup.find("input", {"name": "_token"})
        if token_input:
            token = token_input.get("value")

        # Oyu gonder
        data = {"sehir": SEHIR}
        if token:
            data["csrf_token"] = token

        if proxy:
            proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
            r = session.post(URL, data=data, proxies=proxies, timeout=15)
        else:
            r = session.post(URL, data=data, timeout=15)

        if r.status_code == 200 and ("basarili" in r.text.lower() or "tesekkur" in r.text.lower()):
            print(f"[{sayac}] Oy gonderildi -> {proxy if proxy else 'kendi ip'}")
        else:
            print(f"[{sayac}] Basarisiz -> {proxy if proxy else 'kendi ip'} | Kod: {r.status_code}")

        # Insan gibi rastgele bekle
        time.sleep(random.uniform(3, 8))

    except Exception as e:
        print(f"[{sayac}] Hata: {e}")
        time.sleep(random.uniform(2, 5))

# THREAD WORKER
def worker(kuyruk, sayac):
    while not kuyruk.empty():
        proxy = kuyruk.get()
        oy_ver(proxy, sayac)
        kuyruk.task_done()

def main():
    proxies = proxy_yukle("proxies.txt")
    if not proxies:
        proxies = [None]  # proxy yoksa kendi ip'nden dener

    kuyruk = Queue()
    for p in proxies:
        kuyruk.put(p)

    # 5 thread ile calistir (cok yuksek yapma, ban yersin)
    thread_sayisi = 5
    threads = []
    for i in range(thread_sayisi):
        t = threading.Thread(target=worker, args=(kuyruk, i+1))
        t.start()
        threads.append(t)
        time.sleep(random.uniform(0.3, 1.0))

    for t in threads:
        t.join()

    print("Islem tamamlandi.")

if __name__ == "__main__":
    main()
