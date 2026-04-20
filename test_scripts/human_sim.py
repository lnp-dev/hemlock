import requests

url = "http://localhost:8000/article/1"

# Mimic a real browser
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Sec-Ch-Ua": '"Google Chrome";v="119"',
    "Accept-Encoding": "gzip, deflate, br"
}

def run():
    print("Sending human-like requests to /article/1...")
    for i in range(2):
        response = requests.get(url, headers=headers)
        data = response.json()
        print(f"Request {i+1} Response text:")
        print(data.get("text", data))
        print("-" * 50)
        
if __name__ == "__main__":
    run()
