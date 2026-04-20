import requests
import time
import threading

base_url = "http://localhost:8000"

# Bot headers - typical headless browser lacking richness
bot_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/119.0.0.0 Safari/537.36"
    # Notice no Accept-Language, Sec-CH-UA, Accept-Encoding
}

def fire_request(label=""):
    try:
        res = requests.get(f"{base_url}/article/1", headers=bot_headers)
        data = res.json()
        text = data.get('text', str(data))
        
        # Check for non-ASCII characters (our homoglyphs are cyrillic UTF-8)
        non_ascii_count = sum(1 for c in text if ord(c) > 127)
        poison_status = f"(POISONED: {non_ascii_count} altered chars)" if non_ascii_count > 0 else "(CLEAN)"
        
        print(f"{label} Bot received: {text[:60]}... {poison_status}")
    except Exception as e:
        print("Error:", e)

def trigger_honeypot():
    print("\n[!] Triggering the honeypot: GET /api/hidden-data")
    requests.get(f"{base_url}/api/hidden-data", headers=bot_headers)
    print("Honeypot triggered!")
    time.sleep(1)
    
    # Send another request to verify permanent ban
    print("\n[!] Sending post-honeypot request to /article/2...")
    res = requests.get(f"{base_url}/article/2", headers=bot_headers)
    data = res.json()
    print(f"Post-honeypot response: {data.get('text', str(data))[:60]}...")

if __name__ == "__main__":
    print("--- Phase 0: First-Touch Request (Triggers Layer 0) ---")
    # This single request should trigger the 20% Zero-Trust poisoning immediately
    fire_request()
    time.sleep(1)

    print("\n--- Phase 1: Rapid Firing (Triggers Layer 3) ---")
    threads = []
    # Fire 10 concurrent requests to trip the velocity limit
    for _ in range(10):
        t = threading.Thread(target=fire_request)
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
        
    print("\n--- Phase 2: Honeypot Trigger (Triggers Layer 4) ---")
    trigger_honeypot()
