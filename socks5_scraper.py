import requests
import threading
import socket
import re
from queue import Queue

# Settings
output_file = "proxies.txt"
threads = 50  # Adjust depending on your machine
timeout = 5   # seconds
proxy_sources = [
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt",
    "https://api.proxyscrape.com/?request=getproxies&proxytype=socks5&timeout=5000&country=all&ssl=all&anonymity=all",
    "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt",
]

# Queue to handle proxies
proxy_queue = Queue()

def fetch_proxies():
    proxies = set()
    for url in proxy_sources:
        try:
            print(f"[~] Fetching proxies from {url}")
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                found = re.findall(r'(\d+\.\d+\.\d+\.\d+:\d+)', response.text)
                proxies.update(found)
        except Exception as e:
            print(f"[!] Error fetching {url}: {e}")
    return list(proxies)

def is_socks5_alive(proxy):
    host, port = proxy.split(":")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((host, int(port)))
        # Send SOCKS5 handshake
        sock.sendall(b"\x05\x01\x00")
        data = sock.recv(2)
        sock.close()
        return data and data[0] == 5
    except Exception:
        return False

def worker():
    while not proxy_queue.empty():
        proxy = proxy_queue.get()
        if is_socks5_alive(proxy):
            print(f"[+] Alive SOCKS5: {proxy}")
            with open(output_file, "a") as f:
                f.write(proxy + "\n")
        else:
            print(f"[-] Dead proxy: {proxy}")
        proxy_queue.task_done()

def main():
    # Clean output file
    open(output_file, "w").close()

    print("[*] Fetching proxy list...")
    proxies = fetch_proxies()
    print(f"[*] {len(proxies)} proxies fetched.")

    # Fill the queue
    for proxy in proxies:
        proxy_queue.put(proxy)

    # Start threads
    for _ in range(threads):
        t = threading.Thread(target=worker)
        t.daemon = True
        t.start()

    proxy_queue.join()
    print("[*] Done. Working proxies saved to proxies.txt")

if __name__ == "__main__":
    main()
