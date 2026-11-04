const role = document.body.dataset.role || (location.pathname.includes("/staff/") ? "staff" : location.pathname.includes("/student/") ? "student" : "superadmin");
const layout = role === "staff" ? window.buildStaffLayout : role === "student" ? window.buildStudentLayout : window.buildLayout;
layout("Notifications");
const $ = id => document.getElementById(id);
let items = [];
let unreadOnly = false;

const render = () => {
  const visible = items.filter(item => !unreadOnly || !item.is_read);
  $("sub").textContent = `${items.filter(item => !item.is_read).length} unread`;
  $("list").innerHTML = visible.length
    ? visible.map(item => `<div class="d-flex gap-3 p-3 border-bottom ${item.is_read ? "" : "bg-light"}">
      <span class="ico" style="width:42px;height:42px;border-radius:12px;display:grid;place-items:center;flex:none"><i class="bi bi-megaphone-fill"></i></span>
      <div class="flex-grow-1"><div class="fw-bold">${saEscape(item.title)}${item.is_read ? "" : ' <span class="badge-soft b-blue ms-1">New</span>'}</div>
      <div class="text-secondary small">${saEscape(item.message)}</div><div class="text-secondary" style="font-size:.75rem">${saEscape(item.created_at || "")}</div></div>
      <button class="btn btn-sm btn-link p-0" onclick="markRead(${saEscape(item.id)})" ${item.is_read ? "disabled" : ""}>Mark as read</button></div>`).join("")
    : `<div class="text-center text-secondary py-5">${unreadOnly ? "No unread notifications." : "No notifications."}</div>`;
};

const refresh = async () => {
  const response = await api.get("/notifications/mine");
  items = Array.isArray(response.data) ? response.data : [];
  render();
};

window.markRead = async id => {
  try { await api.post(`/notifications/${id}/read`); await refresh(); }
  catch (error) { saError(error); }
};

$("markAll").onclick = async () => {
  try { await api.post("/notifications/read-all"); await refresh(); }
  catch (error) { saError(error); }
};

document.querySelectorAll('[name="flt"]').forEach(input => {
  input.onchange = () => { unreadOnly = $("fUnread").checked; render(); };
});

saLoading("list");
refresh().catch(error => { saError(error); saEmpty("list", "Unable to load notifications."); });
