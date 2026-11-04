// Shared layout for Staff pages. The sidebar changes with the staff member's role.
const ACADEMY_NAME = "Your Academy";
const ROLE_MENUS = {
  "Trainer": [["dashboard.html","bi-grid-1x2-fill","Dashboard"],["batches.html","bi-collection-fill","My batches"],["attendance.html","bi-calendar-check-fill","Attendance"],["face.html","bi-person-bounding-box","Face attendance"],["marks.html","bi-clipboard-check-fill","Test marks"],["materials.html","bi-folder-fill","Study materials"]],
  "Counselor": [["dashboard.html","bi-grid-1x2-fill","Dashboard"],["leads.html","bi-telephone-inbound-fill","Leads and follow-ups"],["students.html","bi-people-fill","Students and admissions"]],
  "Placement Officer": [["dashboard.html","bi-grid-1x2-fill","Dashboard"],["placements.html","bi-briefcase-fill","Drives, students and companies"],["applications.html","bi-file-earmark-person-fill","Applications"],["readiness.html","bi-bullseye","Placement readiness"]],
  "Accounts": [["dashboard.html","bi-grid-1x2-fill","Dashboard"],["fees.html","bi-cash-coin","Fees, dues and expenses"]]
};
const STAFF_USER = {"Trainer":"Karthik Raj","Counselor":"Anitha M","Placement Officer":"Sowmya T","Accounts":"Divakar P"};

function currentRole(){
  try {
    const raw = localStorage.getItem("user") || sessionStorage.getItem("user");
    const user = raw ? JSON.parse(raw) : null;
    const designation = (user?.designation || "trainer").replace(/_/g, " ");
    const role = designation.replace(/\b\w/g, char => char.toUpperCase());
    return ROLE_MENUS[role] ? role : "Trainer";
  } catch (_) {
    return "Trainer";
  }
}

function buildStaffLayout(pageTitle){
  const role = currentRole(), name = STAFF_USER[role] || "Staff";
  const here = location.pathname.split("/").pop() || "dashboard.html";
  const links = ROLE_MENUS[role].map(([href,icon,label]) =>
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
        <div class="d-flex align-items-center gap-2"><span class="avatar">${name.split(" ").map(w=>w[0]).join("")}</span><div class="d-none d-sm-block lh-sm"><div class="fw-semibold small">${name}</div><div class="text-secondary" style="font-size:.75rem">${role}</div></div></div>
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
  api.requireAuth("staff").then(user => {
    if (!user) return;
    const designation = (user.designation || "trainer").replace(/_/g, " ");
    window.__staffDesignation = designation.replace(/\b\w/g, char => char.toUpperCase());
  }).catch(() => {});
}

// Lets the pages reused from Super Admin call the same function name.
function buildLayout(title){ buildStaffLayout(title); }
