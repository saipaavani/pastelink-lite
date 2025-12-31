import uuid
from flask import Flask, request, jsonify, render_template, abort
from datetime import datetime, timedelta
from config import Config
from models import db, Paste
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["TEST_MODE"] = os.environ.get("TEST_MODE") == "1"


db.init_app(app)

with app.app_context():
    db.create_all()


# ---------- Utility: current time ----------
def get_current_time():
    if app.config["TEST_MODE"]:
        header_time = request.headers.get("x-test-now-ms")
        if header_time:
            return datetime.utcfromtimestamp(int(header_time) / 1000)
    return datetime.utcnow()


# ---------- Health Check ----------
@app.route("/api/healthz", methods=["GET"])
def healthz():
    try:
        db.session.execute(text("SELECT 1"))
        return jsonify({"ok": True})
    except Exception as e:
        print("Health check db error:", e)
        return jsonify({"ok": False, "error" : str(e)})


# ---------- Create Paste (API) ----------
@app.route("/api/pastes", methods=["POST"])
def create_paste():
    # Try JSON first (API)
    data = request.get_json(silent=True)

    # If JSON not present → HTML form
    if data is None:
        data = {
            "content": request.form.get("content"),
            "ttl_seconds": request.form.get("ttl_seconds"),
            "max_views": request.form.get("max_views"),
        }

    # Validate content
    content = data.get("content")
    if not content or not isinstance(content, str):
        return jsonify({"error": "Invalid content"}), 400

    # Parse optional fields
    ttl = data.get("ttl_seconds")
    max_views = data.get("max_views")

    if ttl:
        try:
            ttl = int(ttl)
        except ValueError:
            return jsonify({"error": "Invalid ttl_seconds"}), 400
    else:
        ttl = None

    if max_views:
        try:
            max_views = int(max_views)
        except ValueError:
            return jsonify({"error": "Invalid max_views"}), 400
    else:
        max_views = None

    paste_id = uuid.uuid4().hex[:8]
    now = get_current_time()
    expires_at = now + timedelta(seconds=ttl) if ttl else None

    paste = Paste(
        id=paste_id,
        content=content,
        expires_at=expires_at,
        max_views=max_views
    )

    db.session.add(paste)
    db.session.commit()

    if request.form:
        paste_url = f"{request.host_url}p/{paste_id}"
        return render_template("created.html", paste_url=paste_url)

    # If API → JSON response
    return jsonify({
        "id": paste_id,
        "url": f"{request.host_url}p/{paste_id}"
    }), 201

# ---------- Fetch Paste (API) ----------
@app.route("/api/pastes/<paste_id>", methods=["GET"])
def fetch_paste_api(paste_id):
    paste = Paste.query.get(paste_id)
    now = get_current_time()

    if not paste:
        return jsonify({"error": "Not found"}), 404

    if paste.expires_at and now >= paste.expires_at:
        return jsonify({"error": "Expired"}), 404

    if paste.max_views is not None and paste.view_count >= paste.max_views:
        return jsonify({"error": "View limit exceeded"}), 404

    paste.view_count += 1
    db.session.commit()

    remaining_views = None
    if paste.max_views is not None:
        remaining_views = max(paste.max_views - paste.view_count, 0)

    return jsonify({
        "content": paste.content,
        "remaining_views": remaining_views,
        "expires_at": paste.expires_at.isoformat() if paste.expires_at else None
    }), 200


# ---------- View Paste (HTML) ----------
@app.route("/p/<paste_id>", methods=["GET"])
def view_paste(paste_id):
    paste = Paste.query.get(paste_id)
    now = get_current_time()

    # Not found
    if not paste:
        abort(404)

    # TTL expired
    if paste.expires_at and now >= paste.expires_at:
        db.session.delete(paste)
        db.session.commit()
        abort(404)

    # Max views exceeded
    if paste.max_views is not None and paste.view_count >= paste.max_views:
        db.session.delete(paste)
        db.session.commit()
        abort(404)

    # Increase view count
    paste.view_count += 1
    db.session.commit()

    return render_template("view.html", content=paste.content)



# ---------- Create Paste UI ----------
@app.route("/", methods=["GET"])
def home():
    return render_template("create.html")


# ---------- 404 ----------
@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True)