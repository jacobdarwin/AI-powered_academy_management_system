buildStaffLayout("Study materials");
const $ = id => document.getElementById(id);
let items = [], batches = [];
const formatDate = value => value ? new Date(value).toLocaleDateString("en-IN", {day: "numeric", month: "short", year: "numeric"}) : "-";
const render = () => {
  $("empty").classList.toggle("d-none", items.length > 0);
  $("rows").innerHTML = items.length ? items.map(item => `<tr><td><b>${saEscape(item.title)}</b></td><td>${saEscape(item.material_type || item.type || "-")}</td><td>${saEscape(batches.find(batch => batch.id === item.batch_id)?.code || item.batch_id || "-")}</td><td>${saEscape(formatDate(item.created_at))}</td><td class="text-end"><button class="btn btn-sm btn-outline-danger" onclick="removeMaterial(${saEscape(item.id)})" aria-label="Remove ${saEscape(item.title)}"><i class="bi bi-trash"></i></button></td></tr>`).join("") : `<tr><td colspan="5" class="text-center text-secondary py-4">Nothing shared yet.</td></tr>`;
};
window.removeMaterial = async id => {
  try { await api.delete(`/materials/${id}`); items = items.filter(item => item.id !== id); render(); toast("Material deleted."); }
  catch (error) { toast(error.message || "Unable to delete material.", false); }
};
const toast = (message, ok = true) => { $("toast").className = `toast text-bg-${ok ? "success" : "danger"}`; $("toastMsg").textContent = message; bootstrap.Toast.getOrCreateInstance($("toast")).show(); };
$("form").addEventListener("submit", async event => {
  event.preventDefault(); const form = event.target;
  if (!form.checkValidity()) { form.classList.add("was-validated"); return; }
  try {
    const body = new FormData();
    body.append("title", $("title").value.trim()); body.append("type", $("type").value); body.append("material_type", $("type").value); body.append("batch_id", $("batch").value); body.append("file", $("file").files[0]);
    await api.upload("/materials", body); form.reset(); form.classList.remove("was-validated"); await load(); toast("Material uploaded.");
  } catch (error) { saFormErrors(form, error.errors); toast(error.message || "Unable to upload material.", false); }
});
const load = async () => {
  saLoading("rows");
  try {
    const result = await Promise.all([api.get("/materials"), api.get("/staff/me/batches")]);
    items = result[0].data || []; batches = result[1].data || [];
    $("batch").innerHTML = batches.map(batch => `<option value="${saEscape(batch.id)}">${saEscape(batch.code)}</option>`).join(""); render();
  } catch (error) { saError(error); saEmpty("rows", "Unable to load materials."); }
};
load();
