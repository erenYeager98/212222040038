# main.py
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl
from datetime import datetime, timedelta
from uuid import uuid4
import requests
import pymysql

app = FastAPI()

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
    url: HttpUrl
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
