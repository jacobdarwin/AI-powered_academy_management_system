buildStudentLayout("Timetable");
const $ = id => document.getElementById(id);
const render = data => {
  $("sub").textContent = data.course ? `${saEscape(data.course)} · Batch ${saEscape(data.batch || "")} · Trainer: ${saEscape(data.trainer || "-")}` : "";
  const days = data.days || ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"], slots = data.slots || [];
  $("head").innerHTML = `<tr><th>Time</th>${days.map(day => `<th>${saEscape(day)}</th>`).join("")}</tr>`;
  $("body").innerHTML = slots.length ? slots.map(slot => `<tr><th class="text-nowrap small">${saEscape(slot.time || "-")}</th>${days.map(day => { const item = slot[day] || {}; return `<td><div class="fw-semibold small">${saEscape(item.topic || item.title || "-")}</div><div class="text-secondary" style="font-size:.75rem">${saEscape(item.room || "")}</div></td>`; }).join("")}</tr>`).join("") : `<tr><td colspan="${days.length + 1}" class="text-center text-secondary py-4">No timetable entries.</td></tr>`;
};
saLoading("body"); api.get("/me/timetable").then(response => render(response.data || {})).catch(error => { saError(error); saEmpty("body", "Unable to load timetable."); });
