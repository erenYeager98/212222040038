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
