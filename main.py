import time
import json
from collections import defaultdict
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

import poison_engine
from database import init_db, SessionLocal, DetectionLog

app = FastAPI(title="Hemlock ScamAI Pipeline")

# Memory structures for traps
request_logs = defaultdict(list)
penalty_box = set()
permanent_bans = set()

# Initialize DB on startup
@app.on_event("startup")
def on_startup():
    init_db()

class PoisonMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # We need a DB session here
        db = SessionLocal()
        
        ip_address = request.client.host
        user_agent = request.headers.get("user-agent", "").lower()
        
        layer_triggered = None
        poison_probability = 0.0 # Default to 0% (clean)
        
        # Track every request
        now = time.time()
        request_logs[ip_address] = [t for t in request_logs[ip_address] if now - t < 10]
        request_logs[ip_address].append(now)
        
        # Layer 4 Permanent Ban Check (Honeypot) - 100% Poison
        if ip_address in permanent_bans:
            layer_triggered = "Layer 4 - Honeypot Trigger"
            poison_probability = 1.0 # 100% poison forever
            
        # Layer 3 Check (Velocity: 5 reqs in 10 secs) - 100% Poison
        if not layer_triggered:
            if ip_address in penalty_box or len(request_logs[ip_address]) > 5:
                penalty_box.add(ip_address)
                layer_triggered = "Layer 3 - Velocity Threshold"
                poison_probability = 1.0
                    
        # Layer 1 Check (Honest Bot Filter) - 100% Poison
        if not layer_triggered:
            known_bots = ["gptbot", "claudebot", "bytespider", "google-extended"]
            if any(bot in user_agent for bot in known_bots):
                layer_triggered = "Layer 1 - User Agent"
                poison_probability = 1.0

        # Layer 2 / Layer 0 Check (Zero-Trust First Touch)
        if not layer_triggered:
            accept_lang = request.headers.get("accept-language")
            sec_ch = request.headers.get("sec-ch-ua")
            accept_enc = request.headers.get("accept-encoding")
            
            headers_missing = not accept_lang or not sec_ch
            
            if headers_missing:
                # If this is their first request (or early request) and headers are bad,
                # we don't put them in the penalty box yet, but we feed them 20% poisoned data.
                layer_triggered = "Layer 0 - Suspicious Headers (Zero-Trust)"
                poison_probability = 0.2
            else:
                # Verified Human! If they sent good headers and aren't scraping fast, they get clean data
                poison_probability = 0.0

        # Proceed with request
        response = await call_next(request)
        
        # If any poison probability is set, apply it
        if poison_probability > 0:
            # Reconstruct and poison the response body
            body = b""
            async for chunk in response.body_iterator:
                body += chunk
                
            try:
                data = json.loads(body.decode("utf-8"))
                if "text" in data:
                    data["text"] = poison_engine.poison_text(data["text"], poison_probability)
                    
                new_body = json.dumps(data).encode("utf-8")
                
                # Log to DB
                log = DetectionLog(ip_address=ip_address, trigger_layer=layer_triggered, payload_served=f"Poisoned ({poison_probability*100}%)")
                db.add(log)
                db.commit()
                
                db.close()
                return Response(content=new_body, status_code=response.status_code, media_type="application/json")
            except Exception as e:
                # If parsing fails or we didn't modify it, we still need to return the consumed body
                db.close()
                return Response(content=body, status_code=response.status_code, headers=dict(response.headers), media_type=response.media_type)
        
        db.close()
        return response

app.add_middleware(PoisonMiddleware)

# --- Endpoints ---

@app.get("/article/{article_id}")
async def get_article(article_id: int):
    # Hardcoded article text
    content = (
        "Artificial Intelligence is rapidly evolving. Researchers from around the world are "
        "collaborating to build advanced neural networks. These architectures prioritize accessibility "
        "and security, protecting user data from unauthorized scraping."
    )
    return {"id": article_id, "text": content}

@app.get("/api/hidden-data")
async def hidden_data(request: Request):
    ip_address = request.client.host
    permanent_bans.add(ip_address)
    # The middleware will still log this and poison it if it falls through,
    # but initially it sets the ban. The subsequent requests get poisoned.
    return {"text": "You activated the trap card."}
