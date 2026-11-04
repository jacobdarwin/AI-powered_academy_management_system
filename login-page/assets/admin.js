// Shared layout for Super Admin pages: sidebar + top bar. Add a page by adding one line to MENU.
const ACADEMY_NAME = "Your Academy";
const MENU = [
  ["dashboard.html","bi-grid-1x2-fill","Dashboard"],
  ["leads.html","bi-telephone-inbound-fill","Leads & Admissions"],
  ["students.html","bi-people-fill","Students"],
  ["courses.html","bi-journal-bookmark-fill","Courses & Batches"],
  ["staff.html","bi-person-badge-fill","Trainers & Staff"],
  ["attendance.html","bi-calendar-check-fill","Attendance"],
  ["fees.html","bi-cash-coin","Fees & Accounts"],
  ["placements.html","bi-briefcase-fill","Placements"],
  ["applications.html","bi-file-earmark-person-fill","Placement applications"],
  ["readiness.html","bi-bullseye","Placement readiness"],
  ["forecast.html","bi-graph-up-arrow","Course demand forecast"],
  ["performance.html","bi-award-fill","Staff performance"],
  ["face.html","bi-person-bounding-box","Face attendance"],
  ["reports.html","bi-bar-chart-line-fill","Reports"],
  ["users.html","bi-shield-lock-fill","Users & Roles"],
  ["settings.html","bi-gear-fill","Settings"]
];

function buildLayout(pageTitle){
  api.requireAuth("superadmin").then(user => {
    if (!user) return;
    const name = user.name || user.login_id;
    const identity = document.getElementById("identity");
    const avatar = document.getElementById("avatar");
    const academy = document.querySelector(".brand span:last-child");
    if (identity) identity.innerHTML = `<div class="fw-semibold small">${api.escapeHtml(name)}</div><div class="text-secondary" style="font-size:.75rem">${api.escapeHtml(user.email || user.login_id)}</div>`;
    if (avatar) avatar.textContent = name.split(/\s+/).map(w => w[0]).join("").slice(0, 2).toUpperCase();
    if (academy) academy.textContent = user.academy_name || ACADEMY_NAME;
  }).catch(() => {});
  const here = location.pathname.split("/").pop() || "dashboard.html";
  const links = MENU.map(([href,icon,label]) =>
    `<a class="nav-link ${href===here?"active":""}" href="${href}" ${href===here?'aria-current="page"':""}><i class="bi ${icon}"></i>${label}</a>`).join("");
  document.getElementById("sidebar").innerHTML = `
    <div class="brand"><span class="brand-mark"><i class="bi bi-mortarboard-fill"></i></span><span>${ACADEMY_NAME}</span></div>
    <nav aria-label="Main menu">${links}</nav>
    <div class="side-foot"><a class="nav-link" href="../index.html" id="signOut"><i class="bi bi-box-arrow-left"></i>Sign out</a></div>`;
  document.getElementById("topbar").innerHTML = `
    <div class="d-flex align-items-center gap-3">
      <button class="btn btn-light d-lg-none" id="menuBtn" aria-label="Open menu"><i class="bi bi-list fs-5"></i></button>
      <h1 class="h5 fw-bold mb-0">${pageTitle}</h1>
      <div class="ms-auto d-flex align-items-center gap-3">
        <div class="input-group d-none d-md-flex" style="width:260px"><span class="input-group-text bg-white"><i class="bi bi-search"></i></span><input class="form-control" placeholder="Search students, leads..." aria-label="Search"></div>
        <a class="btn btn-light position-relative" href="notifications.html" aria-label="Notifications"><i class="bi bi-bell"></i><span id="bellCount" class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger">3</span></a>
        <div class="d-flex align-items-center gap-2"><span class="avatar" id="avatar">SA</span><div class="d-none d-sm-block lh-sm" id="identity"><div class="fw-semibold small">Super Admin</div><div class="text-secondary" style="font-size:.75rem">Loading...</div></div></div>
      </div>
    </div>`;
  const sb = document.getElementById("sidebar");
  document.getElementById("menuBtn").onclick = () => sb.classList.toggle("open");
  document.getElementById("backdrop").onclick = () => sb.classList.remove("open");
  document.getElementById("signOut").onclick = event => { event.preventDefault(); api.logout(); };
  api.get("/notifications/unread").then(result => {
    const count = document.getElementById("bellCount");
    if (count) count.textContent = result.meta?.count || 0;
  }).catch(() => {});
}
