// Shared by Super Admin and Staff (Trainer). The camera works in the browser; matching is simulated until the face model is connected.
buildLayout("Face attendance");
const $ = id => document.getElementById(id);
function toast(m, ok = true){ const t = $("toast"); t.className = "toast text-bg-" + (ok ? "success" : "danger"); $("toastMsg").textContent = m; bootstrap.Toast.getOrCreateInstance(t).show(); }
// Sample data: replace with API data later
const BATCHES = {"PFS-12 Morning":["Arun Kumar","Vignesh M","Hari Prasad","Lavanya G","Mukesh R","Sneha J"], "DS-07 Evening":["Divya R","Karan S","Yamini V","Pradeep N"]};
let enrolled = {"Arun Kumar":true,"Vignesh M":true,"Lavanya G":true,"Sneha J":true,"Divya R":true,"Karan S":true};
Object.keys(BATCHES).forEach(b => $("batch").add(new Option(b, b)));
Object.entries(BATCHES).forEach(([b, names]) => names.forEach(n => $("stu").add(new Option(n + " (" + b + ")", n))));
let marks = {}, streams = {};

// ----- camera helpers -----
async function startCam(key, video, msg, frame){
  try {
    streams[key] = await navigator.mediaDevices.getUserMedia({video:{facingMode:"user"}, audio:false});
    video.srcObject = streams[key]; video.hidden = false; await video.play(); msg.hidden = true; frame.classList.remove("d-none"); return true;
  } catch (e) {
    msg.hidden = false; msg.innerHTML = '<i class="bi bi-camera-video-off fs-1"></i><div class="mt-2">Could not open the camera. Allow camera access in the browser, and open this page from localhost or https.</div>'; return false;
  }
}
function stopCam(key, video, msg, frame){
  (streams[key] && streams[key].getTracks().forEach(t => t.stop())); streams[key] = null; video.srcObject = null; video.hidden = true;
  msg.hidden = false; msg.innerHTML = '<i class="bi bi-camera-video fs-1"></i><div class="mt-2">Camera is off</div>'; frame.classList.add("d-none");
}
function wire(key, btn, video, msg, frame, onChange){
  btn.onclick = async () => { if (streams[key]) { stopCam(key, video, msg, frame); btn.textContent = "Start camera"; onChange(false); } else if (await startCam(key, video, msg, frame)) { btn.textContent = "Stop camera"; onChange(true); } };
}
window.addEventListener("pagehide", () => Object.values(streams).forEach(s => s && s.getTracks().forEach(t => t.stop())));

// ----- take attendance -----
function loadBatch(){ marks = {}; BATCHES[$("batch").value].forEach(n => marks[n] = "Absent"); $("result").innerHTML = ""; renderRoster(); }
function renderRoster(){
  const names = BATCHES[$("batch").value], present = names.filter(n => marks[n] !== "Absent").length;
  $("count").textContent = present + " of " + names.length + " present";
  $("roster").innerHTML = names.map(n => `<tr><td><b>${n}</b>${enrolled[n] ? "" : ' <span class="badge-soft b-amber">No face data</span>'}</td>
    <td>${marks[n] === "Absent" ? '<span class="badge-soft b-red">Absent</span>' : '<span class="badge-soft b-green">' + marks[n] + '</span>'}</td>
    <td class="text-end"><button class="btn btn-sm btn-outline-secondary" onclick="manual('${n}')">${marks[n] === "Absent" ? "Mark present" : "Mark absent"}</button></td></tr>`).join("");
}
function manual(n){ marks[n] = marks[n] === "Absent" ? "Present (manual)" : "Absent"; renderRoster(); }
wire("s", $("camBtnS"), $("vS"), $("msgS"), $("frameS"), on => $("scan").disabled = !on);
$("scan").onclick = () => {
  $("scan").disabled = true; $("result").innerHTML = '<span class="text-secondary"><span class="spinner-border spinner-border-sm me-2"></span>Looking for a face...</span>';
  setTimeout(() => {
    const left = BATCHES[$("batch").value].filter(n => marks[n] === "Absent" && enrolled[n]);
    if (!left.length) $("result").innerHTML = '<span class="face-chip" style="background:#dcebf7;color:#1c5a8c"><i class="bi bi-info-circle"></i>Everyone with face data is already marked.</span>';
    else if (Math.random() < 0.2) $("result").innerHTML = '<span class="face-chip" style="background:#f8dedb;color:#b3372f"><i class="bi bi-x-circle"></i>Face not recognised. Try again, or mark manually.</span>';
    else { const n = left[Math.floor(Math.random() * left.length)], c = 90 + Math.floor(Math.random() * 9); marks[n] = "Present (face)"; renderRoster();
      $("result").innerHTML = `<span class="face-chip" style="background:#dff3e8;color:#177a4b"><i class="bi bi-check-circle-fill"></i>${n} · ${c}% match</span>`; }
    $("scan").disabled = !streams.s;
  }, 1200);
};
$("batch").onchange = loadBatch;
$("saveAtt").onclick = () => toast("Attendance saved. " + BATCHES[$("batch").value].filter(n => marks[n] === "Absent").length + " absent.");

// ----- enroll faces -----
let shots = [];
function updEnroll(){ $("capN").textContent = shots.length; $("saveFace").disabled = !(shots.length === 3 && $("consent").checked);
  $("thumbs").innerHTML = shots.map(s => `<img class="thumb" src="${s}" alt="Captured photo">`).join(""); }
function renderEnrolled(){ $("enrolled").innerHTML = Object.entries(BATCHES).flatMap(([b, ns]) => ns.map(n => `<tr><td><b>${n}</b></td><td>${b}</td><td>${enrolled[n] ? '<span class="badge-soft b-green">Enrolled</span>' : '<span class="badge-soft b-amber">Not enrolled</span>'}</td></tr>`)).join(""); }
wire("e", $("camBtnE"), $("vE"), $("msgE"), $("frameE"), on => $("cap").disabled = !on);
$("cap").onclick = () => {
  if (!$("consent").checked) { toast("Tick the consent box first.", false); return; }
  if (shots.length >= 3) return;
  const v = $("vE"), c = document.createElement("canvas"); c.width = 160; c.height = 120; c.getContext("2d").drawImage(v, 0, 0, 160, 120); shots.push(c.toDataURL("image/jpeg", .7)); updEnroll();
};
$("consent").onchange = updEnroll;
$("stu").onchange = () => { shots = []; updEnroll(); };
$("saveFace").onclick = () => { enrolled[$("stu").value] = true; shots = []; updEnroll(); renderEnrolled(); renderRoster(); toast("Face data saved for " + $("stu").value + "."); };
loadBatch(); renderEnrolled(); updEnroll();
