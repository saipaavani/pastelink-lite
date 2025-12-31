👉 Hosted URL: 
https://pastelink-lite.onrender.com

✨ Features
1.Create text pastes instantly
2.Optional TTL (expiry time) in seconds
3. Optional maximum view count
4.Auto-expire pastes after limits are reached Clean, minimal UI
5.Health check endpoint for monitoring

🛠 Tech Stack
1.Backend: Flask (Python)
2.Database: PostgreSQL
3.ORM: SQLAlchemy
4.Frontend: HTML + Bootstrap
5.Deployment: Render
6.Server: Gunicorn

❤️ Health Check

You can verify the service is running by visiting:

/api/healthz

Expected response: 

{ "ok": true }

🧪 Local Setup

1.git clone https://github.com/saipaavani/pastelink-lite
2.cd pastebin-lite
3.pip install -r requirements.txt
4.python app.py

Then open: http://127.0.0.1:5000
