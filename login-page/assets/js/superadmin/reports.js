buildLayout("Reports");
const $ = sa$; let charts = [];
const render = (admissions, fees, attendance) => {
  const total = admissions.stats?.[0]?.value || 0;
  $("stats").innerHTML = `<div class="col-sm-6 col-xl-3"><div class="panel stat"><div><div class="val">${saEscape(total)}</div><div class="lbl">Admissions</div></div></div></div><div class="col-sm-6 col-xl-3"><div class="panel stat"><div><div class="val">${saEscape(fees.length)}</div><div class="lbl">Fee payments</div></div></div></div><div class="col-sm-6 col-xl-3"><div class="panel stat"><div><div class="val">${saEscape(attendance.length)}</div><div class="lbl">Attendance records</div></div></div></div>`;
  const conversion = Array.isArray(admissions.conversion) ? admissions.conversion : [];
  $("conv").innerHTML = conversion.length
    ? conversion.map(item => `<tr><td>${saEscape(item.source)}</td><td>${saEscape(item.leads)}</td><td>${saEscape(item.enrolled)}</td><td>${saEscape(item.conversion)}%</td></tr>`).join("")
    : `<tr><td colspan="4" class="text-center text-secondary py-4">No conversion data.</td></tr>`;
  charts.forEach(chart => chart.destroy()); charts = [];
  if (window.Chart) {
    charts.push(new Chart($("c1"), {type:"bar", data:{labels:fees.map(item => item.receipt_no || ""), datasets:[{label:"Payments", data:fees.map(item => Number(item.amount || 0))}]}, options:{responsive:true, maintainAspectRatio:false}}));
    charts.push(new Chart($("c2"), {type:"bar", data:{labels:admissions.labels || [], datasets:admissions.datasets || []}, options:{responsive:true, maintainAspectRatio:false}}));
    charts.push(new Chart($("c3"), {type:"bar", data:{labels:[...new Set(attendance.map(item => item.date).filter(Boolean))], datasets:[{label:"Attendance records", data:[...new Set(attendance.map(item => item.date).filter(Boolean))].map(date => attendance.filter(item => item.date === date && item.status === "present").length)}]}, options:{responsive:true, maintainAspectRatio:false}}));
  }
};
const load = async () => {
  saLoading("stats"); saLoading("conv");
  const end = new Date(), start = new Date(end);
  start.setMonth(end.getMonth() - Number($("range").value || 6));
  const params = `from=${start.toISOString().slice(0, 10)}&to=${end.toISOString().slice(0, 10)}`;
  try {
    const result = await Promise.all([api.get(`/reports/admissions?${params}`), api.get(`/reports/fees?${params}`), api.get(`/reports/attendance?${params}`)]);
    render(result[0].data || {}, result[1].data || [], result[2].data || []);
  } catch (error) {
    saError(error);
    saEmpty("stats", "Unable to load reports.");
    saEmpty("conv", "Unable to load conversion data.");
  }
};
$("range").onchange = load; load();
