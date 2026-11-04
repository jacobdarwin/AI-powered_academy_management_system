buildStudentLayout("Placement readiness");
const $ = id => document.getElementById(id);
const render = data => {
  const score = Number(data.score ?? data.total ?? 0), color = score >= 80 ? "#177a4b" : score >= 60 ? "#c98512" : "#b3372f", label = score >= 80 ? "Ready" : score >= 60 ? "Almost ready" : "Needs work";
  $("gauge").style.setProperty("--p", score); $("gauge").style.setProperty("--c", color); $("gScore").textContent = score; $("gCat").innerHTML = `<span class="badge-soft ${score >= 80 ? "b-green" : score >= 60 ? "b-amber" : "b-red"}">${saEscape(label)}</span>`; $("gText").textContent = data.summary || "Review the factors below to improve your readiness.";
  const factors = data.factors || {};
  $("factors").innerHTML = Object.entries(factors).length ? Object.entries(factors).map(([key, value]) => `<div class="mb-3"><div class="d-flex justify-content-between small fw-semibold mb-1"><span>${saEscape(key)}</span><span>${saEscape(value)} / 100</span></div><div class="progress"><div class="progress-bar" style="width:${saEscape(value)}%"></div></div></div>`).join("") : `<div class="text-secondary py-3">Readiness factors are unavailable.</div>`;
  $("tips").innerHTML = (data.tips || []).map(tip => `<div class="d-flex gap-3 border-bottom py-3"><div><div class="fw-bold">${saEscape(tip.title || tip)}</div><div class="small text-secondary">${saEscape(tip.description || "")}</div></div></div>`).join("") || `<div class="text-secondary py-3">No readiness tips.</div>`;
};
$("mock").onclick = async () => { try { await api.post("/me/mock-interviews", {}); saToast("Mock interview request sent."); } catch (error) { saError(error); } };
saLoading("factors"); saLoading("tips"); api.get("/me/readiness").then(response => render(response.data || {})).catch(error => { saError(error); saEmpty("factors", "Unable to load readiness."); saEmpty("tips", "Unable to load readiness."); });
