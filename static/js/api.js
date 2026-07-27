/**
 * Hostel Feedback System — API client
 * Thin fetch wrapper — all requests go to the Python Flask backend.
 */

const API = {
  async request(method, path, body) {
    const opts = {
      method,
      credentials: "include",
      headers: { "Content-Type": "application/json" },
    };
    if (body !== undefined) opts.body = JSON.stringify(body);

    const res = await fetch(path, opts);
    const data = await res.json().catch(() => ({}));

    if (!res.ok) {
      const err = new Error(data.error || `HTTP ${res.status}`);
      err.status = res.status;
      err.data   = data;
      throw err;
    }
    return data;
  },

  get:   (path)        => API.request("GET",   path),
  post:  (path, body)  => API.request("POST",  path, body),
  patch: (path, body)  => API.request("PATCH", path, body),
  del:   (path)        => API.request("DELETE", path),
};

/* ── Auth helpers ──────────────────────────────────────── */

async function requireStudent() {
  try {
    const user = await API.get("/api/auth/me");
    return user;
  } catch {
    window.location.href = "/student/login.html";
    return null;
  }
}

async function requireAdmin() {
  try {
    const user = await API.get("/api/auth/admin/me");
    return user;
  } catch {
    window.location.href = "/warden/login.html";
    return null;
  }
}

/* ── UI helpers ────────────────────────────────────────── */

function showAlert(container, message, type = "error") {
  const el = document.createElement("div");
  el.className = `alert alert-${type}`;
  el.textContent = message;
  container.prepend(el);
  setTimeout(() => el.remove(), 5000);
}

function statusBadge(status) {
  const cls = status === "Pending" ? "badge-pending"
            : status === "In Progress" ? "badge-in-progress"
            : "badge-resolved";
  return `<span class="badge ${cls}">${status}</span>`;
}

function formatDate(iso) {
  if (!iso) return "—";
  return new Date(iso).toLocaleDateString("en-IN", {
    day: "2-digit", month: "short", year: "numeric",
    hour: "2-digit", minute: "2-digit",
  });
}

function qs(selector, root = document) { return root.querySelector(selector); }
function qsa(selector, root = document) { return [...root.querySelectorAll(selector)]; }
