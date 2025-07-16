# main.py
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware 
from pydantic import BaseModel, HttpUrl
from datetime import datetime, timedelta
from uuid import uuid4
import requests
import pymysql

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
LOGGING_SERVICE_URL = "http://localhost:5001/log"

# MySQL Database Config
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'dk6969',
    'database': 'url_shortener'
}

def log_event(stack, level, pkg, message):
    try:
        requests.post(LOGGING_SERVICE_URL, json={
            "stack": stack,
            "level": level,
            "pkg": pkg,
            "message": message
        })
    except Exception as e:
        print("Logging failed:", e)

# Initialize DB
def init_db():
    conn = pymysql.connect(**DB_CONFIG)
    with conn.cursor() as c:
        c.execute('''
        CREATE TABLE IF NOT EXISTS shorturls (
            shortcode VARCHAR(20) PRIMARY KEY,
            long_url TEXT NOT NULL,
            created_at DATETIME NOT NULL,
            expiry_at DATETIME NOT NULL,
            clicks INT DEFAULT 0
        )''')
        c.execute('''
        CREATE TABLE IF NOT EXISTS clicks (
            id VARCHAR(36) PRIMARY KEY,
            shortcode VARCHAR(20) NOT NULL,
            timestamp DATETIME NOT NULL,
            referrer TEXT,
            ip VARCHAR(45),
            location VARCHAR(100)
        )''')
    conn.commit()
    conn.close()
    log_event("backend", "info", "db", "Initialized database")

init_db()


class ShortenRequest(BaseModel):
    url: str
    validity: int = 30
    shortcode: str | None = None

@app.post("/shorturls")
def create_short_url(data: ShortenRequest):
    shortcode = data.shortcode or uuid4().hex[:6]
    expiry = datetime.utcnow() + timedelta(minutes=data.validity)
    now = datetime.utcnow()

    conn = pymysql.connect(**DB_CONFIG)
    with conn.cursor() as c:
        c.execute("SELECT 1 FROM shorturls WHERE shortcode=%s", (shortcode,))
        if c.fetchone():
            log_event("backend", "error", "handler", f"Shortcode {shortcode} already exists")
            raise HTTPException(400, detail="Shortcode already taken")

        c.execute("INSERT INTO shorturls (shortcode, long_url, created_at, expiry_at) VALUES (%s, %s, %s, %s)",
                  (shortcode, data.url, now, expiry))
    conn.commit()
    conn.close()

    log_event("backend", "info", "handler", f"Short URL created: {shortcode}")
    return {
        "shortLink": f"http://localhost:8000/{shortcode}",
        "expiry": expiry.isoformat()
    }


@app.get("/{shortcode}")
def redirect_to_url(shortcode: str, request: Request):
    conn = pymysql.connect(**DB_CONFIG)
    with conn.cursor() as c:
        c.execute("SELECT long_url, expiry_at FROM shorturls WHERE shortcode=%s", (shortcode,))
        row = c.fetchone()
        if not row:
            conn.close()
            log_event("backend", "error", "handler", f"Shortcode {shortcode} not found")
            raise HTTPException(404, detail="Shortcode not found")

        long_url, expiry_at = row
        if datetime.utcnow() > expiry_at:
            conn.close()
            log_event("backend", "warn", "handler", f"Shortcode {shortcode} expired")
            raise HTTPException(410, detail="Short URL has expired")

        c.execute("UPDATE shorturls SET clicks = clicks + 1 WHERE shortcode=%s", (shortcode,))
        click_id = str(uuid4())
        timestamp = datetime.utcnow()
        referrer = request.headers.get("referer")
        ip = request.client.host
        location = "India"  # placeholder
        c.execute("INSERT INTO clicks (id, shortcode, timestamp, referrer, ip, location) VALUES (%s, %s, %s, %s, %s, %s)",
                  (click_id, shortcode, timestamp, referrer, ip, location))
    conn.commit()
    conn.close()

    log_event("backend", "info", "handler", f"Redirected {shortcode} to {long_url}")
    return RedirectResponse(url=long_url)

@app.get("/shorturls/{shortcode}")
def get_stats(shortcode: str):
    conn = pymysql.connect(**DB_CONFIG)
    with conn.cursor() as c:
        c.execute("SELECT long_url, created_at, expiry_at, clicks FROM shorturls WHERE shortcode=%s", (shortcode,))
        row = c.fetchone()
        if not row:
            conn.close()
            log_event("backend", "error", "handler", f"Stats not found for {shortcode}")
            raise HTTPException(404, detail="Shortcode not found")

        long_url, created_at, expiry_at, clicks = row
        c.execute("SELECT timestamp, referrer, ip, location FROM clicks WHERE shortcode=%s", (shortcode,))
        click_data = [
            {"timestamp": ts, "referrer": ref, "ip": ip, "location": loc}
            for ts, ref, ip, loc in c.fetchall()
        ]
    conn.close()

    log_event("backend", "info", "handler", f"Stats fetched for {shortcode}")
    return {
        "shortcode": shortcode,
        "original_url": long_url,
        "created_at": created_at.isoformat(),
        "expiry_at": expiry_at.isoformat(),
        "clicks": clicks,
        "click_data": click_data
    }
 