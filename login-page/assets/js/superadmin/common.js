const sa$ = id => document.getElementById(id);
const saEscape = value => api.escapeHtml(value);
const saToast = (message, ok = true) => {
  const node = sa$("toast");
  if (!node) return;
  node.className = `toast text-bg-${ok ? "success" : "danger"}`;
  sa$("toastMsg").textContent = message;
  bootstrap.Toast.getOrCreateInstance(node).show();
};
const saError = error => {
  saToast(error.message || "Request failed.", false);
  return error;
};
const saFormErrors = (form, errors) => {
  Object.entries(errors || {}).forEach(([field, messages]) => {
    const input = form.querySelector(`[name="${field}"],#${field}`);
    if (input) {
      input.setCustomValidity(Array.isArray(messages) ? messages.join(" ") : String(messages));
      input.addEventListener("input", () => input.setCustomValidity(""), {once: true});
    }
  });
};
const saLoading = (id, message = "Loading...") => {
  const node = sa$(id);
  if (!node) return;
  if (node.matches("tbody")) {
    const columns = node.closest("table")?.querySelector("thead tr:last-child")?.children.length || 1;
    node.innerHTML = `<tr><td colspan="${columns}" class="text-center text-secondary py-4">${saEscape(message)}</td></tr>`;
  } else {
    node.innerHTML = `<div class="text-center text-secondary py-4">${saEscape(message)}</div>`;
  }
};
const saEmpty = (id, message = "No records found.") => {
  const node = sa$(id);
  if (!node) return;
  if (node.matches("tbody")) {
    const columns = node.closest("table")?.querySelector("thead tr:last-child")?.children.length || 1;
    node.innerHTML = `<tr><td colspan="${columns}" class="text-center text-secondary py-4">${saEscape(message)}</td></tr>`;
  } else {
    node.innerHTML = `<div class="text-center text-secondary py-4">${saEscape(message)}</div>`;
  }
};
const saCsv = (name, rows) => {
  const csv = rows.map(row => row.map(value => `"${String(value ?? "").replace(/"/g, '""')}"`).join(",")).join("\n");
  const link = document.createElement("a");
  link.href = URL.createObjectURL(new Blob([csv], {type: "text/csv"}));
  link.download = name;
  link.click();
  URL.revokeObjectURL(link.href);
};
