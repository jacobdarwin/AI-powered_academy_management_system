buildLayout("Staff performance");
const $ = sa$; let records = [];
const render = () => {
  const role = $("fRole").value, list = records.filter(item => !role || item.designation === role);
  $("rows").innerHTML = list.length ? list.map(item => `<tr><td><b>${saEscape(item.name)}</b><div class="small text-secondary">${saEscape(item.designation || "")}</div></td><td>-</td><td>-</td><td>-</td><td>-</td><td><span class="text-secondary small">No performance fields available</span></td></tr>`).join("") : `<tr><td colspan="6" class="text-center text-secondary py-4">No staff performance data.</td></tr>`;
  $("sum").innerHTML = `<div class="col-md-4"><div class="panel stat"><div><div class="val">${saEscape(list.length)}</div><div class="lbl">Staff reviewed</div></div></div></div><div class="col-md-4"><div class="panel stat"><div><div class="val">0</div><div class="lbl">Increments approved</div></div></div></div><div class="col-md-4"><div class="panel stat"><div><div class="val">—</div><div class="lbl">Extra salary per month</div></div></div></div>`;
};
const load = async () => { saLoading("rows"); try { records = (await api.get("/reports/staff-performance")).data; const roles = [...new Set(records.map(item => item.designation).filter(Boolean))]; $("fRole").innerHTML = `<option value="">All roles</option>` + roles.map(item => `<option value="${saEscape(item)}">${saEscape(item)}</option>`).join(""); $("bands").textContent = "Performance scoring fields are not provided by the backend."; $("weights").textContent = "Performance weighting is unavailable until scoring fields are added."; render(); } catch (error) { saError(error); saEmpty("rows", "Unable to load performance data."); } };
$("fRole").onchange = render; load();
