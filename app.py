"""
Hostel Feedback System — Flask Backend
Run: python app.py
"""

import os
import sqlite3
from datetime import datetime
from functools import wraps

from flask import Flask, jsonify, request, send_from_directory, session
from werkzeug.security import check_password_hash, generate_password_hash

# ── App setup ────────────────────────────────────────────────────────────────

app = Flask(__name__, static_folder="static", static_url_path="")
app.secret_key = os.environ.get("SECRET_KEY", "hostel-dev-secret-change-in-production")

DATABASE = os.path.join(os.path.dirname(__file__), "hostel.db")

# ── Database helpers ─────────────────────────────────────────────────────────

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.executescript("""
        CREATE TABLE IF NOT EXISTS students (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            name          TEXT    NOT NULL,
            usn           TEXT    UNIQUE NOT NULL,
            email         TEXT    UNIQUE NOT NULL,
            phone         TEXT    DEFAULT '',
            room_number   TEXT    NOT NULL,
            password_hash TEXT    NOT NULL,
            created_at    TEXT    DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS admins (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            username      TEXT    UNIQUE NOT NULL,
            password_hash TEXT    NOT NULL,
            created_at    TEXT    DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS complaints (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id    INTEGER NOT NULL REFERENCES students(id),
            category      TEXT    NOT NULL,
            description   TEXT    NOT NULL,
            status        TEXT    NOT NULL DEFAULT 'Pending',
            warden_notes  TEXT    DEFAULT '',
            created_at    TEXT    DEFAULT (datetime('now')),
            updated_at    TEXT    DEFAULT (datetime('now'))
        );
    """)

    # Seed default warden account
    if not cur.execute("SELECT 1 FROM admins WHERE username='admin'").fetchone():
        cur.execute(
            "INSERT INTO admins (username, password_hash) VALUES (?, ?)",
            ("admin", generate_password_hash("admin123")),
        )

    conn.commit()
    conn.close()


# ── Auth decorators ──────────────────────────────────────────────────────────

def student_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "student_id" not in session:
            return jsonify({"error": "Authentication required"}), 401
        return f(*args, **kwargs)
    return wrapper


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "admin_id" not in session:
            return jsonify({"error": "Authentication required"}), 401
        return f(*args, **kwargs)
    return wrapper


def auth_required(f):
    """Either student or admin."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "student_id" not in session and "admin_id" not in session:
            return jsonify({"error": "Authentication required"}), 401
        return f(*args, **kwargs)
    return wrapper


# ── Static page routes ───────────────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/student/<path:filename>")
def student_pages(filename):
    return send_from_directory("static/student", filename)


@app.route("/warden/<path:filename>")
def warden_pages(filename):
    return send_from_directory("static/warden", filename)


# ── Student auth ─────────────────────────────────────────────────────────────

@app.route("/api/auth/register", methods=["POST"])
def register():
    d = request.get_json(force=True) or {}
    for field in ("name", "usn", "email", "room_number", "password"):
        if not d.get(field, "").strip():
            return jsonify({"error": f"'{field}' is required"}), 400

    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO students (name, usn, email, phone, room_number, password_hash) VALUES (?,?,?,?,?,?)",
            (
                d["name"].strip(),
                d["usn"].strip().upper(),
                d["email"].strip().lower(),
                d.get("phone", "").strip(),
                d["room_number"].strip(),
                generate_password_hash(d["password"]),
            ),
        )
        conn.commit()
        return jsonify({"message": "Registered successfully"}), 201
    except sqlite3.IntegrityError as e:
        msg = str(e)
        if "usn" in msg:
            return jsonify({"error": "USN already registered"}), 409
        if "email" in msg:
            return jsonify({"error": "Email already registered"}), 409
        return jsonify({"error": "Registration failed"}), 409
    finally:
        conn.close()


@app.route("/api/auth/login", methods=["POST"])
def login():
    d = request.get_json(force=True) or {}
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM students WHERE usn=?", (d.get("usn", "").upper(),)
    ).fetchone()
    conn.close()

    if not row or not check_password_hash(row["password_hash"], d.get("password", "")):
        return jsonify({"error": "Invalid USN or password"}), 401

    session.clear()
    session["student_id"]    = row["id"]
    session["student_name"]  = row["name"]
    session["student_usn"]   = row["usn"]
    session["student_room"]  = row["room_number"]
    return jsonify({"id": row["id"], "name": row["name"], "usn": row["usn"], "role": "student"})


@app.route("/api/auth/me")
def me():
    if "student_id" not in session:
        return jsonify({"error": "Not authenticated"}), 401
    return jsonify({
        "id":          session["student_id"],
        "name":        session["student_name"],
        "usn":         session["student_usn"],
        "room_number": session["student_room"],
        "role":        "student",
    })


@app.route("/api/auth/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out"})


# ── Admin auth ───────────────────────────────────────────────────────────────

@app.route("/api/auth/admin/login", methods=["POST"])
def admin_login():
    d = request.get_json(force=True) or {}
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM admins WHERE username=?", (d.get("username", ""),)
    ).fetchone()
    conn.close()

    if not row or not check_password_hash(row["password_hash"], d.get("password", "")):
        return jsonify({"error": "Invalid username or password"}), 401

    session.clear()
    session["admin_id"]       = row["id"]
    session["admin_username"] = row["username"]
    return jsonify({"id": row["id"], "username": row["username"], "role": "admin"})


@app.route("/api/auth/admin/me")
def admin_me():
    if "admin_id" not in session:
        return jsonify({"error": "Not authenticated"}), 401
    return jsonify({
        "id":       session["admin_id"],
        "username": session["admin_username"],
        "role":     "admin",
    })


@app.route("/api/auth/admin/logout", methods=["POST"])
def admin_logout():
    session.clear()
    return jsonify({"message": "Logged out"})


# ── Complaints ───────────────────────────────────────────────────────────────

@app.route("/api/complaints", methods=["GET"])
@auth_required
def list_complaints():
    page   = max(1, int(request.args.get("page", 1)))
    limit  = max(1, min(100, int(request.args.get("limit", 20))))
    offset = (page - 1) * limit
    status = request.args.get("status", "").strip()

    conn = get_db()

    if "admin_id" in session:
        where  = "WHERE 1=1"
        params = []
        if status:
            where  += " AND c.status=?"
            params.append(status)

        rows = conn.execute(
            f"""SELECT c.*, s.name AS student_name, s.usn, s.room_number, s.email, s.phone
                FROM complaints c JOIN students s ON c.student_id=s.id
                {where} ORDER BY c.created_at DESC LIMIT ? OFFSET ?""",
            params + [limit, offset],
        ).fetchall()
        total = conn.execute(
            f"SELECT COUNT(*) FROM complaints c {where}", params
        ).fetchone()[0]
    else:
        sid    = session["student_id"]
        where  = "WHERE c.student_id=?"
        params = [sid]
        if status:
            where  += " AND c.status=?"
            params.append(status)

        rows = conn.execute(
            f"""SELECT c.*, s.name AS student_name, s.usn, s.room_number, s.email, s.phone
                FROM complaints c JOIN students s ON c.student_id=s.id
                {where} ORDER BY c.created_at DESC LIMIT ? OFFSET ?""",
            params + [limit, offset],
        ).fetchall()
        total = conn.execute(
            f"SELECT COUNT(*) FROM complaints c {where}", params
        ).fetchone()[0]

    conn.close()
    return jsonify({
        "complaints": [dict(r) for r in rows],
        "total":      total,
        "page":       page,
        "limit":      limit,
    })


@app.route("/api/complaints", methods=["POST"])
@student_required
def create_complaint():
    d = request.get_json(force=True) or {}
    if not d.get("category") or not d.get("description", "").strip():
        return jsonify({"error": "category and description are required"}), 400

    conn = get_db()
    cur = conn.execute(
        "INSERT INTO complaints (student_id, category, description) VALUES (?,?,?)",
        (session["student_id"], d["category"], d["description"].strip()),
    )
    complaint_id = cur.lastrowid
    conn.commit()

    row = conn.execute(
        """SELECT c.*, s.name AS student_name, s.usn, s.room_number
           FROM complaints c JOIN students s ON c.student_id=s.id
           WHERE c.id=?""",
        (complaint_id,),
    ).fetchone()
    conn.close()
    return jsonify(dict(row)), 201


@app.route("/api/complaints/<int:complaint_id>", methods=["GET"])
@auth_required
def get_complaint(complaint_id):
    conn = get_db()
    row = conn.execute(
        """SELECT c.*, s.name AS student_name, s.usn, s.room_number, s.email, s.phone
           FROM complaints c JOIN students s ON c.student_id=s.id
           WHERE c.id=?""",
        (complaint_id,),
    ).fetchone()
    conn.close()

    if not row:
        return jsonify({"error": "Complaint not found"}), 404

    # Students can only see their own
    if "student_id" in session and row["student_id"] != session["student_id"]:
        return jsonify({"error": "Forbidden"}), 403

    return jsonify(dict(row))


@app.route("/api/complaints/<int:complaint_id>/status", methods=["PATCH"])
@admin_required
def update_status(complaint_id):
    d = request.get_json(force=True) or {}
    status = d.get("status", "").strip()
    notes  = d.get("warden_notes", "").strip()

    allowed = {"Pending", "In Progress", "Resolved"}
    if status not in allowed:
        return jsonify({"error": f"status must be one of {sorted(allowed)}"}), 400

    conn = get_db()
    row = conn.execute("SELECT id FROM complaints WHERE id=?", (complaint_id,)).fetchone()
    if not row:
        conn.close()
        return jsonify({"error": "Complaint not found"}), 404

    conn.execute(
        "UPDATE complaints SET status=?, warden_notes=?, updated_at=datetime('now') WHERE id=?",
        (status, notes, complaint_id),
    )
    conn.commit()

    updated = conn.execute(
        """SELECT c.*, s.name AS student_name, s.usn, s.room_number, s.email, s.phone
           FROM complaints c JOIN students s ON c.student_id=s.id
           WHERE c.id=?""",
        (complaint_id,),
    ).fetchone()
    conn.close()
    return jsonify(dict(updated))


# ── Students (warden only) ───────────────────────────────────────────────────

@app.route("/api/students", methods=["GET"])
@admin_required
def list_students():
    page    = max(1, int(request.args.get("page", 1)))
    limit   = max(1, min(100, int(request.args.get("limit", 20))))
    offset  = (page - 1) * limit
    search  = request.args.get("search", "").strip()

    conn  = get_db()
    where = "WHERE 1=1"
    params= []
    if search:
        where  += " AND (name LIKE ? OR usn LIKE ? OR email LIKE ? OR room_number LIKE ?)"
        like    = f"%{search}%"
        params += [like, like, like, like]

    rows  = conn.execute(
        f"SELECT id,name,usn,email,phone,room_number,created_at FROM students {where} ORDER BY created_at DESC LIMIT ? OFFSET ?",
        params + [limit, offset],
    ).fetchall()
    total = conn.execute(
        f"SELECT COUNT(*) FROM students {where}", params
    ).fetchone()[0]
    conn.close()

    return jsonify({"students": [dict(r) for r in rows], "total": total, "page": page, "limit": limit})


# ── Dashboard stats (warden only) ────────────────────────────────────────────

@app.route("/api/dashboard/stats", methods=["GET"])
@admin_required
def dashboard_stats():
    conn = get_db()
    stats = {
        "total_students":    conn.execute("SELECT COUNT(*) FROM students").fetchone()[0],
        "total_complaints":  conn.execute("SELECT COUNT(*) FROM complaints").fetchone()[0],
        "pending":           conn.execute("SELECT COUNT(*) FROM complaints WHERE status='Pending'").fetchone()[0],
        "in_progress":       conn.execute("SELECT COUNT(*) FROM complaints WHERE status='In Progress'").fetchone()[0],
        "resolved":          conn.execute("SELECT COUNT(*) FROM complaints WHERE status='Resolved'").fetchone()[0],
    }
    recent = conn.execute(
        """SELECT c.id, c.category, c.status, c.created_at, s.name AS student_name, s.room_number
           FROM complaints c JOIN students s ON c.student_id=s.id
           ORDER BY c.created_at DESC LIMIT 5"""
    ).fetchall()
    conn.close()
    stats["recent_complaints"] = [dict(r) for r in recent]
    return jsonify(stats)


# ── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    init_db()
    print("\n✅  Hostel Feedback System running at http://localhost:5000\n")
    print("   Default warden login:  admin / admin123\n")
    app.run(debug=True, port=5000, host="0.0.0.0")
