buildStudentLayout("Placements");
const $ = id => document.getElementById(id);
let drives = [], applications = [], attendance = 0;
const steps = ["Applied", "Shortlisted", "Interview", "Selected"];
const date = value => value ? new Date(value).toLocaleDateString("en-IN", {day: "numeric", month: "short", year: "numeric"}) : "-";
const render = () => {
  $("myAtt").textContent = `${attendance}%`;
  $("drives").innerHTML = drives.length ? drives.map((item, index) => { const application = applications.find(app => app.drive_id === item.id); return `<tr><td><b>${saEscape(item.company_name || item.company_id || "-")}</b></td><td>${saEscape(item.role)}</td><td>${saEscape(date(item.drive_date))}</td><td>${saEscape(item.package || "-")} LPA</td><td>${saEscape(item.attendance_threshold || 0)}% attendance</td><td class="text-end">${application ? `<span class="badge-soft b-green">Applied</span>` : `<button class="btn btn-sm btn-brand" onclick="apply(${saEscape(index)})">Apply</button>`}</td></tr>`; }).join("") : `<tr><td colspan="6" class="text-center text-secondary py-4">No open placement drives.</td></tr>`;
  $("noApps").classList.toggle("d-none", applications.length > 0);
  $("apps").innerHTML = applications.map(app => `<div class="border-bottom py-3"><div class="fw-bold">${saEscape(app.company_name || app.drive_id)} <span class="fw-normal text-secondary">· ${saEscape(app.role || "")}</span></div><div class="d-flex gap-2 flex-wrap mt-2">${steps.map((step, index) => `<span class="badge-soft ${index <= steps.indexOf(app.stage?.replace("_", " ") || "Applied") ? "b-blue" : "b-amber"}">${saEscape(step)}</span>`).join("")}</div></div>`).join("");
};
window.apply = async index => { try { const response = await api.post("/applications", {drive_id: drives[index].id}); applications.unshift(response.data); render(); saToast("Application submitted."); } catch (error) { saError(error); } };
const load = async () => { try { const result = await Promise.all([api.get("/placements/open"), api.get("/me/applications"), api.get("/students?per_page=1")]); drives = result[0].data || []; applications = result[1].data || []; const id = result[2].data[0]?.id; if (id) attendance = Number((await api.get(`/students/${id}/attendance`)).data.percentage || 0); render(); } catch (error) { saError(error); saEmpty("drives", "Unable to load placements."); saEmpty("apps", "Unable to load applications."); } };
saLoading("drives"); saLoading("apps"); load();
