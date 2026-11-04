buildStudentLayout("Dashboard");
const $ = id => document.getElementById(id);
const esc = value => saEscape(value);
const render = data => {
  const student = data.student || {};
  $("hello").textContent = `Welcome back, ${student.name || "Student"}`;
  $("course").textContent = [student.course, student.batch].filter(Boolean).join(" · ");
  const stats = [["bi-calendar-check-fill", "Attendance", `${data.attendance_percentage ?? "-"}%`, "#dff3e8", "#177a4b"], ["bi-cash-coin", "Fee balance", `₹${Number(data.outstanding_dues || 0).toLocaleString("en-IN")}`, "#dcebf7", "#1c5a8c"], ["bi-clipboard-data-fill", "Average marks", `${data.average_marks ?? "-"}%`, "#e3dcf5", "#4c3a96"], ["bi-briefcase-fill", "Open drives", data.open_drives ?? 0, "#fbeccd", "#8a5a06"]];
  $("stats").innerHTML = stats.map(item => `<div class="col-sm-6 col-xl-3"><div class="panel stat"><span class="ico" style="background:${esc(item[3])};color:${esc(item[4])}"><i class="bi ${esc(item[0])}"></i></span><div><div class="val">${esc(item[2])}</div><div class="lbl">${esc(item[1])}</div></div></div></div>`).join("");
  const classes = data.classes || [], deadlines = data.deadlines || [], drives = data.drives || [], news = data.news || [];
  $("classes").innerHTML = classes.length ? classes.map(row => `<tr>${row.map(cell => `<td>${esc(cell)}</td>`).join("")}</tr>`).join("") : `<tr><td colspan="4" class="text-center text-secondary py-4">No classes scheduled.</td></tr>`;
  $("deadlines").innerHTML = deadlines.length ? deadlines.map(item => `<div class="d-flex justify-content-between align-items-center border-bottom py-2"><span class="fw-semibold">${esc(item[0])}</span><span class="badge-soft b-amber">${esc(item[1])}</span></div>`).join("") : `<div class="text-secondary py-3">No deadlines.</div>`;
  $("drives").innerHTML = drives.length ? drives.map(item => `<tr>${item.map(cell => `<td>${esc(cell)}</td>`).join("")}</tr>`).join("") : `<tr><td colspan="5" class="text-center text-secondary py-4">No open drives.</td></tr>`;
  $("news").innerHTML = news.length ? news.map(item => `<div class="border-bottom py-2"><div class="fw-semibold">${esc(item[0])}</div><div class="small text-secondary">${esc(item[1])}</div></div>`).join("") : `<div class="text-secondary py-3">No announcements.</div>`;
};
["stats", "classes", "deadlines", "drives", "news"].forEach(id => saLoading(id));
api.get("/dashboard/student").then(response => render(response.data || {})).catch(error => { saError(error); ["stats", "classes", "deadlines", "drives", "news"].forEach(id => saEmpty(id, "Unable to load dashboard.")); });
