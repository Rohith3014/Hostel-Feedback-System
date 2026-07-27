<<<<<<< HEAD
# 🏠 Hostel Feedback System

A complete hostel complaint management system built with **Python (Flask) + HTML + CSS + JavaScript**.  
No React, no Node.js, no complex setup. Just Python and a browser.

---

## ✨ Features

| Portal | Who | What they can do |
|---|---|---|
| **Student** | Students | Register, login, submit complaints, track status |
| **Warden** | Admin | Dashboard, manage all complaints, update status, view students |

- SQLite database — **no PostgreSQL needed**, works out of the box
- Session-based authentication
- Clean, mobile-friendly UI

---

## 🚀 Run in 3 steps

### Step 1 — Install Python dependencies

```bash
pip install -r requirements.txt
```

> Requires Python 3.8+. Check with: `python --version`

### Step 2 — Start the server

```bash
python app.py
```

### Step 3 — Open in browser

```
http://localhost:5000
```

---

## 🔑 Default Credentials

**Warden / Admin login:**
- Username: `admin`
- Password: `admin123`

**Students:** Register via the Student Portal at http://localhost:5000

---

## 📁 Project Structure

```
hostel-feedback-system/
├── app.py                        # Flask backend (all API routes)
├── requirements.txt              # Python dependencies (flask only)
├── hostel.db                     # SQLite database (auto-created on first run)
├── README.md
├── run.bat                       # Windows one-click start
├── run.sh                        # Mac/Linux one-click start
└── static/
    ├── index.html                # Landing page
    ├── css/
    │   └── main.css              # All styles
    ├── js/
    │   └── api.js                # Fetch wrapper + UI helpers
    ├── student/
    │   ├── login.html
    │   ├── register.html
    │   ├── dashboard.html
    │   ├── complaints.html
    │   ├── new-complaint.html
    │   └── complaint-detail.html
    └── warden/
        ├── login.html
        ├── dashboard.html
        ├── complaints.html
        ├── complaint-detail.html
        └── students.html
```

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3, Flask |
| Database | SQLite (built into Python) |
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Auth | Flask sessions + Werkzeug password hashing |

---

## 🖥 VSCode Tips

1. Install the **Python** extension
2. Open the terminal (`Ctrl+\``) and run `python app.py`
3. Click the link that appears: `http://localhost:5000`

---

## Windows Users

Double-click **`run.bat`** to start the server automatically.

## Mac / Linux Users

Run `./run.sh` in the terminal (first time: `chmod +x run.sh && ./run.sh`).
=======
# Hostel-Feedback-System
impact boys and girsl hostel
>>>>>>> c88000124594039a460c2deffd01781fe58a9cb7
