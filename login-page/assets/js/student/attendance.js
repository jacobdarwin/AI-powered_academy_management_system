buildStudentLayout("Attendance");
const $ = id => document.getElementById(id);
let month = new Date();
let records = [];
const render = () => {
  const title = month.toLocaleDateString("en-IN", {month: "long", year: "numeric"});
  $("mTitle").textContent = title;
  const byDate = Object.fromEntries(records.map(item => [item.date, item.status]));
  const days = new Date(month.getFullYear(), month.getMonth() + 1, 0).getDate(), first = new Date(month.getFullYear(), month.getMonth(), 1).getDay();
  let html = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].map(day => `<div class="h">${saEscape(day)}</div>`).join("") + "<div></div>".repeat(first);
  const counts = {present: 0, absent: 0, late: 0};
  for (let day = 1; day <= days; day++) { const date = `${month.getFullYear()}-${String(month.getMonth() + 1).padStart(2, "0")}-${String(day).padStart(2, "0")}`, status = byDate[date] || ""; if (status === "present") counts.present++; if (status === "absent") counts.absent++; if (status === "late") counts.late++; html += `<div class="d ${status[0]?.toUpperCase() || ""}" title="${saEscape(status)}">${day}</div>`; }
  $("cal").innerHTML = html;
  const total = counts.present + counts.absent + counts.late, pct = total ? Math.round((counts.present + counts.late) / total * 100) : 0;
  $("stats").innerHTML = [["Attendance this month", `${pct}%`, "bi-percent", "#dcebf7", "#1c5a8c"], ["Present", counts.present, "bi-check-circle-fill", "#dff3e8", "#177a4b"], ["Absent", counts.absent, "bi-x-circle-fill", "#f8dedb", "#b3372f"], ["Late", counts.late, "bi-clock-fill", "#fbeccd", "#8a5a06"]].map(item => `<div class="col-6 col-xl-3"><div class="panel stat"><span class="ico" style="background:${saEscape(item[3])};color:${saEscape(item[4])}"><i class="bi ${saEscape(item[2])}"></i></span><div><div class="val">${saEscape(item[1])}</div><div class="lbl">${saEscape(item[0])}</div></div></div></div>`).join("");
  $("warn").classList.toggle("d-none", pct >= 75);
};
const load = async () => { try { const student = (await api.get("/students?per_page=1")).data[0]; const response = await api.get(`/students/${student.id}/attendance`); records = response.data.records || []; render(); } catch (error) { saError(error); saEmpty("cal", "Unable to load attendance."); saEmpty("stats", "Unable to load attendance."); } };
$("prev").onclick = () => { month.setMonth(month.getMonth() - 1); load(); }; $("next").onclick = () => { month.setMonth(month.getMonth() + 1); load(); };
saLoading("cal"); saLoading("stats"); load();
