// Shared by Super Admin and Staff (Placement Officer).
buildLayout("Placement readiness");
const $ = id => document.getElementById(id);
const W = {marks:30, att:20, asg:15, mock:20, proj:15};
const LABEL = {marks:"Marks", att:"Attendance", asg:"Assignments", mock:"Mock interview", proj:"Resume and projects"};
// Sample data: replace with API data (and the ML model's score) later
let students = [
  {name:"Arun Kumar", batch:"PFS-12", marks:81, att:92, asg:70, mock:60, proj:55},
  {name:"Lavanya G", batch:"PFS-12", marks:90, att:95, asg:92, mock:85, proj:80},
  {name:"Hari Prasad", batch:"PFS-12", marks:62, att:71, asg:55, mock:40, proj:45},
  {name:"Sneha J", batch:"PFS-12", marks:84, att:90, asg:80, mock:78, proj:70},
  {name:"Mukesh R", batch:"PFS-12", marks:58, att:68, asg:50, mock:35, proj:30},
  {name:"Divya R", batch:"DS-07", marks:79, att:85, asg:75, mock:70, proj:72},
  {name:"Karan S", batch:"DS-07", marks:93, att:93, asg:88, mock:90, proj:85},
  {name:"Pradeep N", batch:"DS-07", marks:55, att:64, asg:48, mock:42, proj:38},
  {name:"Mohammed Imran", batch:"JFS-09", marks:88, att:96, asg:85, mock:82, proj:76},
  {name:"Gokul S", batch:"JFS-09", marks:66, att:73, asg:60, mock:55, proj:50}];
const score = s => Math.round(Object.keys(W).reduce((a,k) => a + s[k] * W[k], 0) / 100);
const cat = p => p >= 80 ? ["Ready","b-green"] : p >= 60 ? ["Almost ready","b-amber"] : ["Needs work","b-red"];
const weakest = s => Object.keys(W).sort((a,b) => s[a] - s[b])[0];
[...new Set(students.map(s => s.batch))].forEach(b => $("fBatch").add(new Option(b, b)));
let filter = "";
const cell = v => `<td class="${v<60?"down fw-semibold":""}">${v}</td>`;
function render(){
  const q = $("q").value.trim().toLowerCase();
  const all = students.map(s => ({...s, p:score(s)}));
  const counts = {Ready:0, "Almost ready":0, "Needs work":0}; all.forEach(s => counts[cat(s.p)[0]]++);
  $("chips").innerHTML = [["", "All", all.length], ...Object.entries(counts).map(([k,n]) => [k,k,n])].map(([k,l,n]) => `
    <div class="col"><button class="panel w-100 text-start ${filter===k?"border-success border-2":""}" data-c="${k}" style="min-width:110px"><div class="h4 fw-bold mb-0">${n}</div><div class="small text-secondary">${l}</div></button></div>`).join("");
  document.querySelectorAll("[data-c]").forEach(b => b.onclick = () => { filter = b.dataset.c; render(); });
  const list = all.filter(s => (!q || s.name.toLowerCase().includes(q)) && (!$("fBatch").value || s.batch === $("fBatch").value) && (!filter || cat(s.p)[0] === filter)).sort((a,b) => b.p - a.p);
  $("empty").classList.toggle("d-none", list.length > 0);
  $("rows").innerHTML = list.map(s => `<tr><td><b>${s.name}</b><div class="small text-secondary">${s.batch}</div></td>
    <td><div class="small fw-semibold mb-1">${s.p} / 100</div><div class="progress" role="progressbar" aria-label="Readiness" aria-valuenow="${s.p}" aria-valuemin="0" aria-valuemax="100"><div class="progress-bar" style="width:${s.p}%"></div></div></td>
    <td><span class="badge-soft ${cat(s.p)[1]}">${cat(s.p)[0]}</span></td><td>${LABEL[weakest(s)]}</td>${["marks","att","asg","mock","proj"].map(k => cell(s[k])).join("")}</tr>`).join("");
}
["q","fBatch"].forEach(id => $(id).addEventListener("input", render));
$("exp").onclick = () => {
  const rows = [["Student","Batch","Score","Status","Weakest area"], ...students.map(s => [s.name, s.batch, score(s), cat(score(s))[0], LABEL[weakest(s)]])];
  const csv = rows.map(r => r.map(c => `"${String(c).replace(/"/g,'""')}"`).join(",")).join("\n");
  const a = document.createElement("a"); a.href = URL.createObjectURL(new Blob([csv], {type:"text/csv"})); a.download = "placement-readiness.csv"; a.click();
};
render();
