buildStaffLayout("My profile");
const $ = id => document.getElementById(id);
const toast = (message, ok = true) => { $("toast").className = `toast text-bg-${ok ? "success" : "danger"}`; $("toastMsg").textContent = message; bootstrap.Toast.getOrCreateInstance($("toast")).show(); };
const load = async () => {
  try {
    const user = (await api.get("/staff/me")).data || {};
    $("who").value = `${user.name || user.login_id || ""} (${user.designation || "Staff"})`;
    $("phone").value = user.phone || ""; $("email").value = user.email || "";
  } catch (error) { saError(error); }
};
$("f1").addEventListener("submit", async event => {
  event.preventDefault(); const form = event.target;
  if (!form.checkValidity()) { form.classList.add("was-validated"); return; }
  try { await api.patch("/staff/me", {name: $("who").value.split(" (")[0], phone: $("phone").value.trim(), email: $("email").value.trim()}); toast("Profile saved."); }
  catch (error) { saFormErrors(form, error.errors); toast(error.message || "Unable to save profile.", false); }
});
const checkMatch = () => $("p2").setCustomValidity($("p2").value === $("p1").value ? "" : "Passwords do not match.");
$("p1").addEventListener("input", checkMatch); $("p2").addEventListener("input", checkMatch);
$("f2").addEventListener("submit", async event => {
  event.preventDefault(); const form = event.target; checkMatch();
  if (!form.checkValidity()) { form.classList.add("was-validated"); return; }
  try { await api.post("/auth/change-password", {current_password: $("p0").value, new_password: $("p1").value}); form.reset(); form.classList.remove("was-validated"); toast("Password updated."); }
  catch (error) { saFormErrors(form, error.errors); toast(error.message || "Unable to update password.", false); }
});
load();
