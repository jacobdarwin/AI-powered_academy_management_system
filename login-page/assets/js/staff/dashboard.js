buildStaffLayout("Dashboard");
const $ = id => document.getElementById(id);
const escape = value => saEscape(value);

const render = data => {
  const cards = [
    ["bi-people-fill", "Active students", data.students ?? 0],
    ["bi-collection-fill", "Running batches", data.active_batches ?? 0],
    ["bi-briefcase-fill", "Upcoming drives", data.drives?.length ?? 0],
    ["bi-person-lines-fill", "Open leads", data.leads ?? 0]
  ];
  $("stats").innerHTML = cards.map(item => `<div class="col-sm-6 col-xl-3"><div class="panel stat"><span class="ico"><i class="bi ${escape(item[0])}"></i></span><div><div class="val">${escape(item[2])}</div><div class="lbl">${escape(item[1])}</div></div></div></div>`).join("");
  $("t1Title").textContent = "Upcoming drives";
  $("t1Head").innerHTML = "<tr><th>Company</th><th>Date</th><th>Applications</th></tr>";
  $("t1Body").innerHTML = data.drives?.length
    ? data.drives.map(row => `<tr>${row.map(cell => `<td>${escape(cell)}</td>`).join("")}</tr>`).join("")
    : `<tr><td colspan="3" class="text-center text-secondary py-4">No upcoming drives.</td></tr>`;
  $("actions").innerHTML = [["applications.html", "bi-file-earmark-check", "Review applications"], ["placements.html", "bi-calendar-plus", "View placements"], ["notifications.html", "bi-bell", "View notifications"]]
    .map(item => `<a href="${escape(item[0])}"><i class="bi ${escape(item[1])}"></i>${escape(item[2])}</a>`).join("");
  $("t2Title").textContent = "Pending dues";
  $("t2").innerHTML = data.dues?.length
    ? data.dues.map(row => `<div class="d-flex justify-content-between align-items-center border-bottom py-2"><span class="fw-semibold">${escape(row[0])}</span><span class="badge-soft b-amber">${escape(row[2])}</span></div>`).join("")
    : `<div class="text-secondary py-3">No pending dues.</div>`;
};

["stats", "t1Body", "t2"].forEach(id => saLoading(id));
api.get("/dashboard/staff")
  .then(response => render(response.data || {}))
  .catch(error => {
    saError(error);
    ["stats", "t1Body", "t2"].forEach(id => saEmpty(id, "Unable to load dashboard data."));
  });
