buildStaffLayout("My batches");
const $ = id => document.getElementById(id);
let batches = [];

const render = () => {
  $("cards").innerHTML = batches.length ? batches.map((batch, index) => `<div class="col-md-6"><div class="panel h-100">
    <div class="d-flex justify-content-between align-items-start"><div><h3 class="h5 fw-bold mb-0">${saEscape(batch.code)}</h3><div class="text-secondary small">${saEscape(batch.course_name || batch.course_id || "-")} · ${saEscape(batch.time || batch.schedule || "-")}</div></div><span class="badge-soft b-blue">${saEscape(batch.student_count ?? 0)} students</span></div>
    <div class="small mt-3">Start date: <b>${saEscape(batch.start_date || "-")}</b></div>
    <div class="d-flex justify-content-between small mt-3 mb-1"><span>Capacity</span><b>${saEscape(batch.capacity ?? "-")}</b></div>
    <div class="d-flex gap-2 mt-3"><button class="btn btn-sm btn-brand" onclick="showStudents(${saEscape(index)})">View students</button><a class="btn btn-sm btn-outline-secondary" href="attendance.html">Mark attendance</a></div></div></div>`).join("")
    : `<div class="col-12 text-center text-secondary py-4">No batches assigned.</div>`;
};

window.showStudents = async index => {
  const batch = batches[index];
  try {
    const response = await api.get(`/batches/${batch.id}/students?per_page=100`);
    $("mT").textContent = `${batch.code} students`;
    $("stuRows").innerHTML = response.data.length
      ? response.data.map(student => `<tr><td><b>${saEscape(student.name)}</b></td><td>${saEscape(student.attendance_percentage ?? "-")}%</td><td>${saEscape(student.average_marks ?? "-")}%</td></tr>`).join("")
      : `<tr><td colspan="3" class="text-center text-secondary py-4">No students in this batch.</td></tr>`;
    bootstrap.Modal.getOrCreateInstance($("stuModal")).show();
  } catch (error) {
    saError(error);
    $("stuRows").innerHTML = `<tr><td colspan="3" class="text-center text-secondary py-4">Unable to load students.</td></tr>`;
  }
};

saLoading("cards");
api.get("/staff/me/batches")
  .then(response => { batches = Array.isArray(response.data) ? response.data : []; render(); })
  .catch(error => { saError(error); $("cards").innerHTML = `<div class="col-12 text-center text-secondary py-4">Unable to load assigned batches.</div>`; });
