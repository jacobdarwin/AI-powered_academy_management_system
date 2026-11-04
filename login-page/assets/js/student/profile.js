buildStudentLayout("My profile");
const $ = id => document.getElementById(id);
const toast = (message, ok = true) => { $("toast").className = `toast text-bg-${ok ? "success" : "danger"}`; $("toastMsg").textContent = message; bootstrap.Toast.getOrCreateInstance($("toast")).show(); };
const render = me => {
  const initials = saEscape(String(me.name || "").split(/\s+/).map(word => word[0]).join(""));
  $("photoBox").textContent = initials; $("pName").textContent = me.name || ""; $("pId").textContent = me.student_code || me.login_id || "";
  $("fixed").innerHTML = [["Course", me.course_name || me.course_id || "-"], ["Batch", me.batch_code || me.batch_id || "-"], ["Date of birth", me.date_of_birth || "-"], ["Joined", me.admission_date || "-"]].map(item => `<div class="d-flex justify-content-between border-bottom py-2"><dt class="text-secondary fw-normal mb-0">${saEscape(item[0])}</dt><dd class="fw-semibold mb-0">${saEscape(item[1])}</dd></div>`).join("") + `<p class="text-secondary mt-3 mb-0">To change your name, course or batch, contact the academy office.</p>`;
  $("phone").value = me.phone || ""; $("email").value = me.email || ""; $("parent").value = me.guardian_phone || ""; $("addr").value = me.address || "";
};
const load = async () => { try { render((await api.get("/me/profile")).data || {}); } catch (error) { saError(error); } };
$("photo").onchange = async event => { const file = event.target.files[0]; if (!file) return; if (file.size > 2 * 1024 * 1024) { toast("Choose a photo smaller than 2 MB.", false); return; } try { const formData = new FormData(); formData.append("photo", file); await api.upload("/me/profile/photo", formData); toast("Photo updated."); } catch (error) { saError(error); } };
$("f1").addEventListener("submit", async event => { event.preventDefault(); const form = event.target; if (!form.checkValidity()) { form.classList.add("was-validated"); return; } try { await api.patch("/me/profile", {phone: $("phone").value.trim(), email: $("email").value.trim(), guardian_phone: $("parent").value.trim(), address: $("addr").value.trim()}); toast("Profile saved."); } catch (error) { saFormErrors(form, error.errors); toast(error.message || "Unable to save profile.", false); } });
const match = () => $("p2").setCustomValidity($("p2").value === $("p1").value ? "" : "Passwords do not match.");
$("p1").addEventListener("input", match); $("p2").addEventListener("input", match);
$("f2").addEventListener("submit", async event => { event.preventDefault(); const form = event.target; match(); if (!form.checkValidity()) { form.classList.add("was-validated"); return; } try { await api.post("/auth/change-password", {current_password: $("p0").value, new_password: $("p1").value}); form.reset(); toast("Password updated."); } catch (error) { saFormErrors(form, error.errors); toast(error.message || "Unable to update password.", false); } });
load();
