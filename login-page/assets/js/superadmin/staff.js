buildLayout("Trainers & Staff");
const $ = sa$;
let staff = [], workloads = [];
const render = () => {
  const query = $("q").value.trim().toLowerCase(), role = $("fRole").value;
  const list = staff.filter(item => (!query || `${item.name} ${item.phone || ""}`.toLowerCase().includes(query)) && (!role || item.designation === role));
  $("count").textContent = `${list.length} staff`; $("empty").classList.toggle("d-none", list.length > 0);
  $("rows").innerHTML = list.map(item => `<tr><td><div class="d-flex align-items-center gap-2"><span class="s-avatar">${saEscape(item.name.split(/\s+/).map(word => word[0]).join("").slice(0, 2))}</span><b>${saEscape(item.name)}</b></div></td><td>${saEscape(item.designation)}</td><td>${saEscape(item.phone || "-")}</td><td>${saEscape(item.joined_on || "-")}</td><td>-</td><td><span class="badge-soft ${item.status === "active" ? "b-green" : "b-red"}">${saEscape(item.status)}</span></td></tr>`).join("");
  $("loadCards").innerHTML = workloads.length ? workloads.map(item => `<div class="col-md-6 col-xl-3"><div class="panel h-100"><b>${saEscape(item.name || item.staff_name || "-")}</b><div class="small text-secondary mt-2">${saEscape(item.active_batches ?? item.batch_count ?? 0)} batches</div></div></div>`).join("") : `<div class="col-12 text-center text-secondary py-4">No workload data.</div>`;
};
const load = async () => {
  saLoading("rows"); saLoading("loadCards");
  try { const result = await Promise.all([api.get("/staff?per_page=100"), api.get("/staff/workload")]); staff = result[0].data; workloads = result[1].data; const roles = [...new Set(staff.map(item => item.designation).filter(Boolean))]; $("fRole").innerHTML = `<option value="">All roles</option>` + roles.map(item => `<option value="${saEscape(item)}">${saEscape(item)}</option>`).join(""); $("sRole").innerHTML = roles.map(item => `<option value="${saEscape(item)}">${saEscape(item)}</option>`).join(""); render(); }
  catch (error) { saError(error); saEmpty("rows", "Unable to load staff."); saEmpty("loadCards", "Unable to load workload."); }
};
$("staffForm").addEventListener("submit", async event => {
  event.preventDefault(); const form = event.target; if (!form.checkValidity()) { form.classList.add("was-validated"); return; }
  try { const email = `${$("sName").value.trim().toLowerCase().replace(/\s+/g, ".")}@academy.local`, password = crypto.randomUUID().replace(/-/g, "").slice(0, 12); const user = await api.post("/users", {name:$("sName").value.trim(), email, role:"staff", password}); await api.post("/staff", {user_id:user.data.id, name:$("sName").value.trim(), phone:$("sPhone").value.trim(), designation:$("sRole").value, staff_code:`STF-${Date.now().toString().slice(-6)}`, joined_on:$("sJoin").value, qualification:$("sSkill").value.trim()}); bootstrap.Modal.getInstance($("staffModal")).hide(); form.reset(); await load(); saToast("Staff added."); }
  catch (error) { saFormErrors(form, error.errors); saError(error); }
});
["q", "fRole"].forEach(id => $(id).addEventListener("input", render)); load();
