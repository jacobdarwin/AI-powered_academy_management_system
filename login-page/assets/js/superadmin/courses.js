buildLayout("Courses & Batches");
const $ = sa$;
let courses = [], batches = [], trainers = [];
const load = async () => {
  saLoading("courseCards"); saLoading("batchRows");
  try {
    const result = await Promise.all([api.get("/courses?per_page=100"), api.get("/batches?per_page=100"), api.get("/staff?per_page=100")]);
    courses = result[0].data; batches = result[1].data; trainers = result[2].data;
    $("count").textContent = `${courses.length} courses, ${batches.length} batches`;
    $("courseCards").innerHTML = courses.length ? courses.map(course => `<div class="col-md-6 col-xl-4"><div class="panel h-100"><div class="d-flex justify-content-between"><h3 class="h5 fw-bold">${saEscape(course.name)}</h3><span class="badge-soft ${course.is_active ? "b-green" : "b-red"}">${course.is_active ? "Active" : "Inactive"}</span></div><div class="small text-secondary">${saEscape(course.code || "")}</div><div class="mt-3">${saEscape(course.duration_months)} months · ₹${saEscape(course.total_fee)}</div><div class="small text-secondary mt-2">${saEscape(course.description || "")}</div></div></div>`).join("") : `<div class="col-12 text-center text-secondary py-4">No courses found.</div>`;
    $("batchRows").innerHTML = batches.length ? batches.map(batch => `<tr><td><b>${saEscape(batch.code)}</b></td><td>${saEscape(courses.find(item => item.id === batch.course_id)?.name || "-")}</td><td>${saEscape(trainers.find(item => item.id === batch.trainer_id)?.name || "-")}</td><td>${saEscape(batch.time ?? batch.schedule ?? "-")}</td><td>${saEscape(batch.start_date || "-")}</td><td>${saEscape(batch.seats ?? batch.capacity ?? 0)}</td><td>${saEscape(batch.status)}</td></tr>`).join("") : `<tr><td colspan="7" class="text-center text-secondary py-4">No batches found.</td></tr>`;
    $("bCourse").innerHTML = courses.map(item => `<option value="${saEscape(item.id)}">${saEscape(item.name)}</option>`).join("");
    $("bTrainer").innerHTML = trainers.filter(item => item.status === "active").map(item => `<option value="${saEscape(item.id)}">${saEscape(item.name)}</option>`).join("");
  } catch (error) { saError(error); saEmpty("courseCards", "Unable to load courses."); saEmpty("batchRows", "Unable to load batches."); }
};
$("courseForm").addEventListener("submit", async event => {
  event.preventDefault(); const form = event.target;
  if (!form.checkValidity()) { form.classList.add("was-validated"); return; }
  try { await api.post("/courses", {name:$("cName").value.trim(), code:$("cName").value.trim().toUpperCase().replace(/\s+/g, "-"), total_fee:Number($("cFee").value), duration_months:Number($("cDur").value), description:$("cTools").value.trim()}); bootstrap.Modal.getInstance($("courseModal")).hide(); form.reset(); await load(); saToast("Course saved."); }
  catch (error) { saFormErrors(form, error.errors); saError(error); }
});
$("batchForm").addEventListener("submit", async event => {
  event.preventDefault(); const form = event.target;
  if (!form.checkValidity()) { form.classList.add("was-validated"); return; }
  try { await api.post("/batches", {code:$("bName").value.trim(), course_id:Number($("bCourse").value), trainer_id:Number($("bTrainer").value), time:$("bTime").value, start_date:$("bStart").value, seats:Number($("bSeats").value)}); bootstrap.Modal.getInstance($("batchModal")).hide(); form.reset(); await load(); saToast("Batch created."); }
  catch (error) { saFormErrors(form, error.errors); saError(error); }
});
load();
