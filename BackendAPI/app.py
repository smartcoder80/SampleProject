from dotenv import load_dotenv
load_dotenv()  # must run before config.py reads os.environ

import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import bcrypt
import jwt
import datetime
import psycopg2.extras
from config import get_db, release_db, SECRET_KEY

app = Flask(__name__)

_allowed_origins = [o.strip() for o in os.environ.get("FRONTEND_URL", "http://localhost:3000").split(",")]
CORS(app, origins=_allowed_origins)


def generate_token(user_id: str, username: str) -> str:
    payload = {
        "user_id": user_id,
        "username": username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def verify_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username", "").strip()
    password = data.get("password", "")
    email = data.get("email", "").strip()

    if not username or not password or not email:
        return jsonify({"error": "Username, email, and password are required"}), 400

    conn = get_db()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT id FROM users WHERE username = %s", (username,))
            if cur.fetchone():
                return jsonify({"error": "Username already exists"}), 409

            hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

            cur.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s) RETURNING id, username",
                (username, email, hashed),
            )
            user = cur.fetchone()
            conn.commit()

        token = generate_token(str(user["id"]), user["username"])
        return jsonify({"token": token, "username": user["username"]}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": "Registration failed", "detail": str(e)}), 500
    finally:
        release_db(conn)


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    conn = get_db()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT id, username, password_hash FROM users WHERE username = %s", (username,))
            user = cur.fetchone()

        if not user:
            return jsonify({"error": "Invalid username or password"}), 401

        if not bcrypt.checkpw(password.encode("utf-8"), user["password_hash"].encode("utf-8")):
            return jsonify({"error": "Invalid username or password"}), 401

        token = generate_token(str(user["id"]), user["username"])
        return jsonify({"token": token, "username": user["username"]}), 200
    except Exception as e:
        return jsonify({"error": "Login failed", "detail": str(e)}), 500
    finally:
        release_db(conn)


@app.route("/api/me", methods=["GET"])
def me():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return jsonify({"error": "Missing or invalid token"}), 401

    payload = verify_token(auth_header[7:])
    if not payload:
        return jsonify({"error": "Token expired or invalid"}), 401

    conn = get_db()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                "SELECT id, username, email, created_at FROM users WHERE username = %s",
                (payload["username"],),
            )
            user = cur.fetchone()

        if not user:
            return jsonify({"error": "User not found"}), 404

        user["id"] = str(user["id"])
        user["created_at"] = user["created_at"].isoformat() if user["created_at"] else None
        return jsonify(dict(user)), 200
    except Exception as e:
        return jsonify({"error": "Failed to fetch user", "detail": str(e)}), 500
    finally:
        release_db(conn)


@app.route("/api/logout", methods=["POST"])
def logout():
    # JWT is stateless; the client discards the token.
    return jsonify({"message": "Logged out successfully"}), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)
