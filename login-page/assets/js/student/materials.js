buildStudentLayout("Study materials");
const $ = id => document.getElementById(id);
const ICON = {Notes: ["bi-file-earmark-text-fill", "#dcebf7", "#1c5a8c"], Video: ["bi-play-circle-fill", "#f8dedb", "#b3372f"], Practice: ["bi-pencil-square", "#dff3e8", "#177a4b"]};
let items = [];
const render = () => {
  const query = $("q").value.trim().toLowerCase(), type = $("type").value, visible = items.filter(item => (!query || String(item.title).toLowerCase().includes(query)) && (!type || item.material_type === type));
  $("empty").classList.toggle("d-none", visible.length > 0);
  $("list").innerHTML = visible.length ? visible.map(item => { const icon = ICON[item.material_type] || ICON.Notes; return `<div class="col-md-6 col-xl-4"><div class="panel h-100"><div class="d-flex gap-3"><span class="ico" style="width:46px;height:46px;border-radius:12px;display:grid;place-items:center;font-size:1.3rem;flex:none;background:${saEscape(icon[1])};color:${saEscape(icon[2])}"><i class="bi ${saEscape(icon[0])}"></i></span><div><div class="fw-bold">${saEscape(item.title)}</div><div class="small text-secondary">${saEscape(item.material_type || "-")} · ${saEscape(item.file_size || "-")}</div><div class="small text-secondary">${saEscape(item.created_at || "")}</div></div></div><button class="btn btn-sm btn-outline-secondary mt-3" onclick="downloadMaterial(${saEscape(item.id)})"><i class="bi bi-download me-1"></i>Download</button></div></div>`; }).join("") : `<div class="col-12 text-center text-secondary py-4">No materials found.</div>`;
};
window.downloadMaterial = async id => { try { const response = await api.get(`/materials/${id}/download`); const link = document.createElement("a"); link.href = URL.createObjectURL(new Blob([response.data])); link.download = "material"; link.click(); URL.revokeObjectURL(link.href); } catch (error) { saError(error); } };
["q", "type"].forEach(id => $(id).addEventListener("input", render));
saLoading("list");
api.get("/me/materials").then(response => { items = response.data || []; render(); }).catch(error => { saError(error); saEmpty("list", "Unable to load materials."); });
