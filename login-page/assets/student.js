// Shared layout for Student pages.
const ACADEMY_NAME = "Your Academy";
const STUDENT = {name:"Arun Kumar", id:"STU-2026-001", course:"Python Full Stack", batch:"PFS-12 Morning"};
const S_MENU = [
  ["dashboard.html","bi-grid-1x2-fill","Dashboard"],["timetable.html","bi-calendar3","Timetable"],["attendance.html","bi-calendar-check-fill","Attendance"],
  ["fees.html","bi-cash-coin","Fees"],["marks.html","bi-clipboard-data-fill","Marks and assignments"],["materials.html","bi-folder-fill","Study materials"],
  ["placements.html","bi-briefcase-fill","Placements"],["readiness.html","bi-bullseye","Placement readiness"],["assistant.html","bi-chat-dots-fill","Ask AI assistant"],["certificates.html","bi-award-fill","Certificates"]
];
function buildStudentLayout(pageTitle){
  api.requireAuth("student").then(user => {
    if (!user) return;
    const identity = document.getElementById("studentIdentity");
    const avatar = document.getElementById("studentAvatar");
    if (identity) identity.innerHTML = `<div class="fw-semibold small">${api.escapeHtml(user.name || user.login_id)}</div><div class="text-secondary" style="font-size:.75rem">${api.escapeHtml(user.login_id)}</div>`;
    if (avatar) avatar.textContent = (user.name || user.login_id).split(/\s+/).map(w => w[0]).join("").slice(0, 2).toUpperCase();
  }).catch(() => {});
  const here = location.pathname.split("/").pop() || "dashboard.html";
  const links = S_MENU.map(([href,icon,label]) =>
    `<a class="nav-link ${href===here?"active":""}" href="${href}" ${href===here?'aria-current="page"':""}><i class="bi ${icon}"></i>${label}</a>`).join("");
  document.getElementById("sidebar").innerHTML = `
    <div class="brand"><span class="brand-mark"><i class="bi bi-mortarboard-fill"></i></span><span>${ACADEMY_NAME}</span></div>
    <nav aria-label="Main menu">${links}</nav>
    <div class="side-foot"><a class="nav-link" href="profile.html"><i class="bi bi-person-circle"></i>My profile</a><a class="nav-link" href="../index.html" id="signOut"><i class="bi bi-box-arrow-left"></i>Sign out</a></div>`;
  document.getElementById("topbar").innerHTML = `
    <div class="d-flex align-items-center gap-3">
      <button class="btn btn-light d-lg-none" id="menuBtn" aria-label="Open menu"><i class="bi bi-list fs-5"></i></button>
      <h1 class="h5 fw-bold mb-0">${pageTitle}</h1>
      <div class="ms-auto d-flex align-items-center gap-3">
        <a class="btn btn-light position-relative" href="notifications.html" aria-label="Notifications"><i class="bi bi-bell"></i><span id="bellCount" class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger">2</span></a>
        <div class="d-flex align-items-center gap-2"><span class="avatar" id="studentAvatar">${STUDENT.name.split(" ").map(w=>w[0]).join("")}</span><div class="d-none d-sm-block lh-sm" id="studentIdentity"><div class="fw-semibold small">${STUDENT.name}</div><div class="text-secondary" style="font-size:.75rem">${STUDENT.id}</div></div></div>
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
