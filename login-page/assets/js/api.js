(function () {
  const API_BASE = window.ACADEMY_API_BASE || "/api/v1";
  const storage = () => localStorage.getItem("token") ? localStorage : sessionStorage;

  class ApiError extends Error {
    constructor(message, status, errors) {
      super(message);
      this.name = "ApiError";
      this.status = status;
      this.errors = errors || {};
    }
  }

  async function request(path, options = {}, retry = true) {
    const headers = new Headers(options.headers || {});
    headers.set("Accept", "application/json");
    if (options.body && !(options.body instanceof FormData)) headers.set("Content-Type", "application/json");
    const token = storage().getItem("token");
    if (token) headers.set("Authorization", `Bearer ${token}`);
    const response = await fetch(`${API_BASE}${path}`, {...options, headers});
    if (response.status === 401 && retry && storage().getItem("refresh_token")) {
      const refreshed = await fetch(`${API_BASE}/auth/refresh`, {
        method: "POST",
        headers: {Authorization: `Bearer ${storage().getItem("refresh_token")}`}
      });
      if (refreshed.ok) {
        const body = await refreshed.json();
        storage().setItem("token", body.data.access_token);
        return request(path, options, false);
      }
      localStorage.removeItem("token");
      localStorage.removeItem("refresh_token");
      sessionStorage.removeItem("token");
      sessionStorage.removeItem("refresh_token");
      if (!/\/(?:index|forgot-password)\.html?$/.test(window.location.pathname)) {
        window.location.href = "/index.html";
      }
    }
    const contentType = response.headers.get("content-type") || "";
    const body = contentType.includes("application/json")
      ? await response.json().catch(() => ({}))
      : await response.text();
    if (!contentType.includes("application/json")) {
      if (!response.ok) throw new ApiError("Request failed", response.status);
      return {success: true, data: body, message: "", meta: {}};
    }
    if (!response.ok || body.success === false) throw new ApiError(body.message || "Request failed", response.status, body.errors);
    return body;
  }

  window.api = {
    API_BASE,
    ApiError,
    get: path => request(path),
    post: (path, data) => request(path, {method: "POST", body: JSON.stringify(data)}),
    put: (path, data) => request(path, {method: "PUT", body: JSON.stringify(data)}),
    patch: (path, data) => request(path, {method: "PATCH", body: JSON.stringify(data)}),
    delete: path => request(path, {method: "DELETE"}),
    upload: (path, formData) => request(path, {method: "POST", body: formData}),
    async requireAuth(allowedRole) {
      if (!storage().getItem("token")) {
        window.location.href = "../index.html";
        return null;
      }
      const response = await request("/auth/me");
      if (allowedRole && response.data.role !== allowedRole) {
        window.location.href = "../index.html";
        return null;
      }
      return response.data;
    },
    async logout() {
      try { await request("/auth/logout", {method: "POST"}); } finally {
        localStorage.clear(); sessionStorage.clear(); window.location.href = "../index.html";
      }
    },
    escapeHtml(value) {
      return String(value ?? "").replace(/[&<>"']/g, char => ({
        "&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#039;"
      }[char]));
    }
  };
})();

window.sa$ = window.sa$ || (id => document.getElementById(id));
window.saEscape = window.saEscape || (value => window.api.escapeHtml(value));
window.saToast = window.saToast || ((message, ok = true) => {
  const node = window.sa$("toast");
  if (!node) return;
  node.className = `toast text-bg-${ok ? "success" : "danger"}`;
  window.sa$("toastMsg").textContent = message;
  bootstrap.Toast.getOrCreateInstance(node).show();
});
window.saError = window.saError || (error => {
  window.saToast(error.message || "Request failed.", false);
  return error;
});
window.saFormErrors = window.saFormErrors || ((form, errors) => {
  Object.entries(errors || {}).forEach(([field, messages]) => {
    const input = form.querySelector(`[name="${field}"],#${field}`);
    if (input) {
      input.setCustomValidity(Array.isArray(messages) ? messages.join(" ") : String(messages));
      input.addEventListener("input", () => input.setCustomValidity(""), {once: true});
    }
  });
});
window.saLoading = window.saLoading || ((id, message = "Loading...") => {
  const node = window.sa$(id);
  if (!node) return;
  if (node.matches("tbody")) {
    const columns = node.closest("table")?.querySelector("thead tr:last-child")?.children.length || 1;
    node.innerHTML = `<tr><td colspan="${columns}" class="text-center text-secondary py-4">${window.saEscape(message)}</td></tr>`;
  } else {
    node.innerHTML = `<div class="text-center text-secondary py-4">${window.saEscape(message)}</div>`;
  }
});
window.saEmpty = window.saEmpty || ((id, message = "No records found.") => {
  const node = window.sa$(id);
  if (!node) return;
  if (node.matches("tbody")) {
    const columns = node.closest("table")?.querySelector("thead tr:last-child")?.children.length || 1;
    node.innerHTML = `<tr><td colspan="${columns}" class="text-center text-secondary py-4">${window.saEscape(message)}</td></tr>`;
  } else {
    node.innerHTML = `<div class="text-center text-secondary py-4">${window.saEscape(message)}</div>`;
  }
});
window.saCsv = window.saCsv || ((name, rows) => {
  const csv = rows.map(row => row.map(value => `"${String(value ?? "").replace(/"/g, '""')}"`).join(",")).join("\n");
  const link = document.createElement("a");
  link.href = URL.createObjectURL(new Blob([csv], {type: "text/csv"}));
  link.download = name;
  link.click();
  URL.revokeObjectURL(link.href);
});
