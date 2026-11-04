buildLayout("Students");
const $ = sa$;
let students = [], courses = [], batches = [];
const initials = name => saEscape(String(name || "").split(/\s+/).map(word => word[0]).slice(0, 2).join("").toUpperCase());
const render = () => {
  const query = $("q").value.trim().toLowerCase(), course = $("fCourse").value, status = $("fStatus").value.toLowerCase(), fee = $("fFees").value;
  const list = students.filter(student => (!query || `${student.name} ${student.student_code} ${student.phone || ""}`.toLowerCase().includes(query)) && (!course || String(student.course_id) === course) && (!status || student.status === status) && (!fee || fee === "All fees"));
  $("count").textContent = `${list.length} of ${students.length} students`; $("empty").classList.toggle("d-none", list.length > 0);
  $("rows").innerHTML = list.map(student => `<tr><td><div class="d-flex align-items-center gap-2"><span class="s-avatar">${initials(student.name)}</span><div class="lh-sm"><b>${saEscape(student.name)}</b><div class="text-secondary small">${saEscape(student.student_code)}</div></div></div></td><td>${saEscape(courses.find(item => item.id === student.course_id)?.name || "-")}<div class="text-secondary small">${saEscape(batches.find(item => item.id === student.batch_id)?.code || "-")}</div></td><td>${saEscape(student.phone || "-")}</td><td>-</td><td>-</td><td><span class="badge-soft b-blue">${saEscape(student.status)}</span></td><td class="text-end"><button class="btn btn-sm btn-outline-secondary" onclick="openProfile(${saEscape(student.id)})">View</button></td></tr>`).join("");
};
const load = async () => {
  saLoading("rows");
  try { const result = await Promise.all([api.get("/students?per_page=100"), api.get("/courses?per_page=100"), api.get("/batches?per_page=100")]); students = result[0].data; courses = result[1].data; batches = result[2].data; $("fCourse").innerHTML = `<option value="">All courses</option>` + courses.map(item => `<option value="${saEscape(item.id)}">${saEscape(item.name)}</option>`).join(""); $("fCourseAdd").innerHTML = courses.map(item => `<option value="${saEscape(item.id)}">${saEscape(item.name)}</option>`).join(""); $("fCourseAdd").dispatchEvent(new Event("change")); render(); }
  catch (error) { saError(error); saEmpty("rows", "Unable to load students."); }
};
$("fCourseAdd").onchange = () => { $("fBatch").innerHTML = batches.filter(item => String(item.course_id) === $("fCourseAdd").value).map(item => `<option value="${saEscape(item.id)}">${saEscape(item.code)}</option>`).join(""); };
window.openProfile = async id => { try { const student = students.find(item => item.id === id); const summary = await api.get(`/students/${id}/summary`); $("pName").textContent = student?.name || "Student"; $("pBody").innerHTML = `<div class="mb-3"><b>${saEscape(student?.student_code)}</b><div class="text-secondary">${saEscape(student?.email || "")}</div></div><div>Attendance: ${saEscape(summary.data.attendance_percentage ?? summary.data.percentage ?? "-")}%</div>`; bootstrap.Offcanvas.getOrCreateInstance($("profile")).show(); } catch (error) { saError(error); } };
$("addForm").addEventListener("submit", async event => {
  event.preventDefault(); const form = event.target; if (!form.checkValidity()) { form.classList.add("was-validated"); return; }
  try { const email = $("fEmail").value.trim(), password = crypto.randomUUID().replace(/-/g, "").slice(0, 12); const user = await api.post("/users", {name:$("fName").value.trim(), email, role:"student", password}); const year = new Date().getFullYear(); await api.post("/students", {user_id:user.data.id, student_code:`STU-${year}-${String(Date.now()).slice(-6)}`, name:$("fName").value.trim(), email, phone:$("fPhone").value.trim(), course_id:Number($("fCourseAdd").value), batch_id:Number($("fBatch").value), admission_date:$("fDob").value, guardian_phone:$("fParent").value.trim(), address:$("fAddr").value.trim()}); bootstrap.Modal.getInstance($("addModal")).hide(); form.reset(); await load(); saToast("Student added."); }
  catch (error) { saFormErrors(form, error.errors); saError(error); }
});
["q", "fCourse", "fStatus", "fFees"].forEach(id => $(id).addEventListener("input", render));
$("exportBtn").onclick = async () => { try { const response = await api.get("/students/export?format=csv"); const link = document.createElement("a"); link.href = URL.createObjectURL(new Blob([response.data], {type:"text/csv"})); link.download = "students.csv"; link.click(); } catch (error) { saError(error); } };
load();
