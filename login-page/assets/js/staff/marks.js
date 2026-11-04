buildStaffLayout("Test marks");
const $ = id => document.getElementById(id);
let batches = [], students = [], marks = {};
const toast = (message, ok = true) => { $("toast").className = `toast text-bg-${ok ? "success" : "danger"}`; $("toastMsg").textContent = message; bootstrap.Toast.getOrCreateInstance($("toast")).show(); };

const render = () => {
  const max = Number($("max").value) || 1;
  $("rows").innerHTML = students.length ? students.map(student => {
    const value = marks[student.id] ?? "";
    const percentage = value === "" ? null : Math.round(Number(value) / max * 100);
    return `<tr><td><b>${saEscape(student.name)}</b></td><td><input type="number" min="0" max="${saEscape(max)}" class="form-control form-control-sm" aria-label="Marks for ${saEscape(student.name)}" value="${saEscape(value)}" oninput="setMark(${saEscape(student.id)}, this.value)"></td><td>${percentage === null ? "-" : `<span class="badge-soft ${percentage >= 75 ? "b-green" : percentage >= 50 ? "b-amber" : "b-red"}">${saEscape(percentage)}%</span>`}</td></tr>`;
  }).join("") : `<tr><td colspan="3" class="text-center text-secondary py-4">No students in this batch.</td></tr>`;
  const values = Object.values(marks).filter(value => value !== "").map(Number);
  $("sum").innerHTML = [["Marks entered", `${values.length} of ${students.length}`], ["Class average", values.length ? `${Math.round(values.reduce((a, b) => a + b, 0) / values.length / max * 100)}%` : "-"], ["Highest", values.length ? `${Math.max(...values)} / ${max}` : "-"]]
    .map(item => `<div class="col-md-4"><div class="panel"><div class="val fw-bold fs-4">${saEscape(item[1])}</div><div class="text-secondary small">${saEscape(item[0])}</div></div></div>`).join("");
};
window.setMark = (id, value) => { marks[id] = Number(value) > Number($("max").value) ? "" : value; render(); };
const loadStudents = async () => {
  saLoading("rows");
  try {
    const response = await api.get(`/batches/${$("batch").value}/students?per_page=100`);
    students = response.data || []; marks = {}; render();
  } catch (error) { saError(error); saEmpty("rows", "Unable to load students."); }
};
$("batch").onchange = loadStudents;
$("max").oninput = render;
$("save").onclick = async () => {
  const form = $("test").form;
  if (!$("test").value.trim()) { $("test").setCustomValidity("Enter the test name."); form?.reportValidity(); return; }
  try {
    const assessment = await api.post("/assessments", {batch_id: Number($("batch").value), title: $("test").value.trim(), type: "test", assessment_type: "test", max_marks: Number($("max").value), date: new Date().toISOString().slice(0, 10)});
    await api.post("/marks/bulk", {assessment_id: assessment.data.id, records: Object.entries(marks).filter(([, value]) => value !== "").map(([student_id, value]) => ({student_id: Number(student_id), marks: Number(value)}))});
    toast("Marks saved.");
  } catch (error) { saFormErrors(form || document.body, error.errors); toast(error.message || "Unable to save marks.", false); }
};
saLoading("rows");
api.get("/staff/me/batches").then(response => {
  batches = response.data || [];
  $("batch").innerHTML = batches.map(batch => `<option value="${saEscape(batch.id)}">${saEscape(batch.code)}</option>`).join("");
  return batches.length ? loadStudents() : null;
}).catch(error => { saError(error); saEmpty("rows", "Unable to load assigned batches."); });
