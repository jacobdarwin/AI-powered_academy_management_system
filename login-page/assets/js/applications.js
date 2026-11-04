const role = document.body.dataset.role || "superadmin";
const layout = role === "staff" ? window.buildStaffLayout : role === "student" ? window.buildStudentLayout : window.buildLayout;
layout("Placement applications");
const $ = id => document.getElementById(id);
let applications = [], students = [], drives = [], companies = [], stage = "";
const stages = ["applied", "shortlisted", "interview", "selected", "rejected"];
const listData = response => Array.isArray(response.data) ? response.data : [];

const render = () => {
  const query = $("q").value.trim().toLowerCase();
  const companyId = $("fCo").value;
  const filtered = applications.filter(item => {
    const drive = drives.find(value => value.id === item.drive_id);
    const student = students.find(value => value.id === item.student_id);
    return (!query || `${student?.name || item.student_id}`.toLowerCase().includes(query)) &&
      (!companyId || String(drive?.company_id) === companyId) &&
      (!stage || item.stage === stage);
  });
  $("pipe").innerHTML = [["", "All"], ...stages.map(value => [value, value])].map(([key, label]) =>
    `<div class="col"><button class="panel w-100 text-start ${stage === key ? "border-success border-2" : ""}" data-stage="${saEscape(key)}">
      <div class="h4 fw-bold mb-0">${saEscape(applications.filter(item => !key || item.stage === key).length)}</div>
      <div class="small text-secondary">${saEscape(label)}</div></button></div>`).join("");
  document.querySelectorAll("[data-stage]").forEach(button => button.onclick = () => { stage = button.dataset.stage; render(); });
  $("empty").classList.toggle("d-none", filtered.length > 0);
  $("rows").innerHTML = filtered.map(item => {
    const drive = drives.find(value => value.id === item.drive_id);
    const company = companies.find(value => value.id === drive?.company_id);
    const student = students.find(value => value.id === item.student_id);
    return `<tr><td><b>${saEscape(student?.name || item.student_id)}</b></td>
      <td>${saEscape(company?.name || "-")}<div class="text-secondary small">${saEscape(drive?.role || "")}</div></td>
      <td>-</td><td>${saEscape(drive?.drive_date || "-")}</td><td>-</td>
      <td><select class="form-select form-select-sm" onchange="updateApplication(${saEscape(item.id)},this.value)">
        ${stages.map(value => `<option value="${saEscape(value)}" ${value === item.stage ? "selected" : ""}>${saEscape(value)}</option>`).join("")}
      </select></td></tr>`;
  }).join("");
};

const load = async () => {
  $("rows").innerHTML = `<tr><td colspan="6" class="text-center text-secondary py-4">Loading...</td></tr>`;
  try {
    const result = await Promise.all([
      api.get("/applications?per_page=100"),
      api.get("/students?per_page=100"),
      api.get("/drives?per_page=100"),
      api.get("/companies?per_page=100")
    ]);
    applications = listData(result[0]); students = listData(result[1]);
    drives = listData(result[2]); companies = listData(result[3]);
    $("fCo").innerHTML = `<option value="">All companies</option>` +
      companies.map(item => `<option value="${saEscape(item.id)}">${saEscape(item.name)}</option>`).join("");
    render();
  } catch (error) {
    saError(error);
    $("rows").innerHTML = `<tr><td colspan="6" class="text-center text-secondary py-4">Unable to load applications.</td></tr>`;
  }
};

window.updateApplication = async (id, status) => {
  try { await api.patch(`/applications/${id}`, {status}); await load(); saToast("Application updated."); }
  catch (error) { saError(error); }
};

$("q").addEventListener("input", render);
$("fCo").addEventListener("input", render);
$("exp").onclick = () => saCsv("shortlisted.csv", [
  ["Student", "Company", "Stage"],
  ...applications.filter(item => ["shortlisted", "interview", "selected"].includes(item.stage)).map(item => {
    const drive = drives.find(value => value.id === item.drive_id);
    return [
      students.find(value => value.id === item.student_id)?.name || item.student_id,
      companies.find(value => value.id === drive?.company_id)?.name || "",
      item.stage
    ];
  })
]);

load();
