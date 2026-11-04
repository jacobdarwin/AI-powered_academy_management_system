buildStudentLayout("Certificates");
const $ = id => document.getElementById(id);
const date = value => value ? new Date(value).toLocaleDateString("en-IN", {day: "numeric", month: "long", year: "numeric"}) : "-";
let certificates = [];
const render = eligibility => {
  $("final").innerHTML = `<p class="text-secondary small mb-3">${saEscape(eligibility.course_name || eligibility.course_id || "-")}</p><div class="d-flex justify-content-between align-items-center border-bottom py-2"><span>Eligibility</span><span>${eligibility.eligible ? "Eligible" : "Not eligible"}</span></div><button class="btn btn-brand mt-3" id="finalBtn" ${eligibility.eligible ? "" : "disabled"}>Download certificate</button>`;
  if (eligibility.eligible) $("finalBtn").onclick = () => saToast("Certificate download is not available until a certificate is issued.", false);
  $("list").innerHTML = certificates.length ? certificates.map(item => `<div class="col-md-6 col-xl-4"><div class="panel h-100"><div class="fw-bold">${saEscape(item.certificate_no)}</div><div class="small text-secondary">${saEscape(date(item.issued_on))}</div><button class="btn btn-sm btn-outline-secondary mt-3" onclick="downloadCertificate(${saEscape(item.id)})">Download</button></div></div>`).join("") : `<div class="col-12 text-center text-secondary py-4">No certificates issued.</div>`;
};
window.downloadCertificate = async id => { try { const response = await api.get(`/certificates/${id}/download`); const link = document.createElement("a"); link.href = URL.createObjectURL(new Blob([response.data], {type: "application/pdf"})); link.download = "certificate.pdf"; link.click(); URL.revokeObjectURL(link.href); } catch (error) { saError(error); } };
saLoading("final"); saLoading("list");
Promise.all([api.get("/certificates/eligibility"), api.get("/me/certificates")]).then(result => { certificates = result[1].data || []; render(result[0].data || {}); }).catch(error => { saError(error); saEmpty("final", "Unable to load certificate eligibility."); saEmpty("list", "Unable to load certificates."); });
