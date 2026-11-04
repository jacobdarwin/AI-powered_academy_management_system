buildLayout("Course demand forecast");
const $ = sa$; let report = {};
const render = () => {
  const forecast = report.forecast || [];
  $("cards").innerHTML = `<div class="col-md-4"><div class="panel stat"><div><div class="val">${saEscape(forecast[0]?.next_month ?? "-")}</div><div class="lbl">Expected next month</div></div></div></div><div class="col-md-4"><div class="panel stat"><div><div class="val">${saEscape(forecast[0]?.next_three_months ?? "-")}</div><div class="lbl">Expected next 3 months</div></div></div></div><div class="col-md-4"><div class="panel"><div class="small text-secondary">Forecasts are estimates from available admissions history.</div></div></div>`;
  const months = report.labels || [], values = report.datasets?.[0]?.data || [];
  $("fhead").innerHTML = `<tr><th>Period</th><th>Admissions</th></tr>`;
  $("frows").innerHTML = months.length ? months.map((month, index) => `<tr><td>${saEscape(month)}</td><td>${saEscape(values[index] ?? 0)}</td></tr>`).join("") : `<tr><td colspan="2" class="text-center text-secondary py-4">No forecast data.</td></tr>`;
  if (window.Chart && $("chart")) new Chart($("chart"), {type:"line", data:{labels:months, datasets:report.datasets || []}, options:{responsive:true, maintainAspectRatio:false}});
};
const load = async () => { saLoading("cards"); saLoading("frows"); try { report = (await api.get("/reports/course-demand")).data || {}; render(); } catch (error) { saError(error); saEmpty("cards", "Unable to load forecast."); saEmpty("frows", "Unable to load forecast."); } };
load();
