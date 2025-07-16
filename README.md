# 212222040038

A HTTP URL Shortener built using FastAPI + MySQL. Supports custom shortcodes, expiry, click tracking, and logging integration.

---

##  Features

- Shorten long URLs with optional custom codes
- Expiry-based redirection (default: 30 mins)
- Click tracking with IP, referrer & geo-location
- REST API with FastAPI
- MySQL as database
- Logs all events to external logging service

---

## ⚙️ Setup Instructions

1. Clone the repo
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3.Run backend using uvicorn and Frontend using npm run dev (created using vite)
4. Test the endpoints.


## Screenshots
### Frontend
<img width="938" height="312" alt="Screenshot 2025-07-16 163914" src="https://github.com/user-attachments/assets/9f4790b2-fd10-4b05-b0da-bb287af3ac5d" />
<img width="900" height="309" alt="Screenshot 2025-07-16 164216" src="https://github.com/user-attachments/assets/e45d96cd-09f1-4c2f-99ae-a47b8d678a1d" />
<img width="1292" height="426" alt="Screenshot 2025-07-16 164304" src="https://github.com/user-attachments/assets/e2dbcc8a-efca-4043-b9e0-ad69e63b321b" />

### Backend
<img width="639" height="145" alt="image" src="https://github.com/user-attachments/assets/2d4df9ec-265e-40c0-8ab9-83dd172878de" />

<img width="432" height="286" alt="image" src="https://github.com/user-attachments/assets/b88bd7ec-8a01-4b0c-b7c2-cec280bc6f29" />
