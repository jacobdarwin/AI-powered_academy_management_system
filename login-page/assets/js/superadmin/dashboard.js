buildLayout("Dashboard");
const $ = sa$; let charts = [];
$("today").textContent = new Date().toLocaleDateString("en-IN", {weekday:"long", day:"numeric", month:"long", year:"numeric"});
const render = data => {
  const cards = [["bi-people-fill","Active students",data.students],["bi-journal-bookmark-fill","Running batches",data.active_batches],["bi-collection","Courses",data.courses],["bi-person-lines-fill","Open leads",data.leads]];
  $("stats").innerHTML = cards.map(item => `<div class="col-sm-6 col-xl-3"><div class="panel stat"><span class="ico"><i class="bi ${item[0]}"></i></span><div><div class="val">${saEscape(item[2])}</div><div class="lbl">${saEscape(item[1])}</div></div></div></div>`).join("");
  const fill = (id, rows, message) => { $(id).innerHTML = rows?.length ? rows.map(row => `<tr>${row.map(cell => `<td>${saEscape(cell)}</td>`).join("")}</tr>`).join("") : `<tr><td colspan="5" class="text-center text-secondary py-4">${saEscape(message)}</td></tr>`; };
  fill("admissions", data.recent_admissions, "No recent admissions.");
  fill("drives", data.drives, "No upcoming drives.");
  fill("dues", data.dues, "No pending fees.");
  charts.forEach(chart => chart.destroy()); charts = [];
  if (data.admissions_series && $("mainChart")) charts.push(new Chart($("mainChart"), {type:"bar", data:{labels:data.admissions_series.labels || [], datasets:data.admissions_series.datasets || []}, options:{responsive:true, maintainAspectRatio:false}}));
  if (data.lead_series && $("leadChart")) charts.push(new Chart($("leadChart"), {type:"doughnut", data:{labels:data.lead_series.labels || [], datasets:data.lead_series.datasets || []}, options:{responsive:true, maintainAspectRatio:false}}));
};
saLoading("stats"); ["admissions","drives","dues"].forEach(id => saLoading(id));
api.get("/dashboard/superadmin").then(response => render(response.data || {})).catch(error => { saError(error); ["stats","admissions","drives","dues"].forEach(id => saEmpty(id, "Unable to load dashboard data.")); });
