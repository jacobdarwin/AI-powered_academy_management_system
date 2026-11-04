buildStudentLayout("Fees");
const $ = id => document.getElementById(id);
const money = value => `₹${Number(value || 0).toLocaleString("en-IN")}`;
const date = value => value ? new Date(value).toLocaleDateString("en-IN", {day: "numeric", month: "short", year: "numeric"}) : "-";
let history = [];
const render = data => {
  const plans = data.installments || data.plans || [], total = plans.reduce((sum, item) => sum + Number(item.amount || 0), 0), paid = plans.reduce((sum, item) => sum + Number(item.paid_amount || 0), 0);
  $("stats").innerHTML = [["Total fees", money(total), "bi-cash-stack", "#dcebf7", "#1c5a8c"], ["Paid", money(paid), "bi-check-circle-fill", "#dff3e8", "#177a4b"], ["Balance", money(total - paid), "bi-hourglass-split", total > paid ? "#fbeccd" : "#dff3e8", total > paid ? "#8a5a06" : "#177a4b"]].map(item => `<div class="col-md-4"><div class="panel stat"><span class="ico" style="background:${saEscape(item[3])};color:${saEscape(item[4])}"><i class="bi ${saEscape(item[2])}"></i></span><div><div class="val">${saEscape(item[1])}</div><div class="lbl">${saEscape(item[0])}</div></div></div></div>`).join("");
  $("inst").innerHTML = plans.length ? plans.map(item => `<tr><td><b>${saEscape(item.title || item.name || "Installment")}</b></td><td>${saEscape(date(item.due_date))}</td><td>${saEscape(money(item.amount))}</td><td>${saEscape(item.status || "Pending")}</td></tr>`).join("") : `<tr><td colspan="4" class="text-center text-secondary py-4">No fee plans found.</td></tr>`;
  $("hist").innerHTML = history.length ? history.map(item => `<div class="d-flex justify-content-between align-items-center border-bottom py-2"><div><b>${saEscape(item.receipt_no)}</b><div class="small text-secondary">${saEscape(date(item.created_at))} · ${saEscape(item.mode)}</div></div><div class="text-end"><div class="fw-semibold">${saEscape(money(item.amount))}</div><button class="btn btn-sm btn-link p-0" onclick="receipt(${saEscape(item.id)})">Print receipt</button></div></div>`).join("") : `<div class="text-secondary py-3">No payments found.</div>`;
  $("payBtn").disabled = total <= paid; if (total <= paid) $("payBtn").textContent = "No payment due";
};
window.receipt = async id => { try { const response = await api.get(`/payments/${id}/receipt?format=json`); const item = response.data; const win = window.open("", "_blank", "width=520,height=600"); win.document.write(`<body style="font-family:sans-serif;padding:32px"><h2>${saEscape("Academy")}</h2><p>Receipt: ${saEscape(item.receipt_no)}</p><p>Amount: ${saEscape(money(item.amount))}</p></body>`); win.document.close(); win.print(); } catch (error) { saError(error); } };
$("payBtn").onclick = () => saToast("Online payment is not available in the current API contract.", false);
["stats", "inst", "hist"].forEach(id => saLoading(id));
Promise.all([api.get("/me/fees"), api.get("/me/payments")]).then(result => { history = result[1].data || []; render(result[0].data || {}); }).catch(error => { saError(error); ["stats", "inst", "hist"].forEach(id => saEmpty(id, "Unable to load fees.")); });
