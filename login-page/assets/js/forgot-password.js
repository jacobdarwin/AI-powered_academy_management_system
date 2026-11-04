

















const $ = id => document.getElementById(id);
const form = $("resetForm");

form.addEventListener("submit", async e => {
  e.preventDefault();
  if (!form.checkValidity()) { form.classList.add("was-validated"); return; }
  $("sendBtn").disabled = true; $("spin").classList.remove("d-none");
  try {
    await api.post("/auth/forgot-password", { identifier: $("who").value.trim() });
  } finally {
    $("sendBtn").disabled = false; $("spin").classList.add("d-none");
  }
  // Same message whether or not the account exists, so nobody can check who has an account.
  $("shown").textContent = $("who").value.trim();
  $("step1").classList.add("d-none"); $("step2").classList.remove("d-none");
});

$("again").onclick = () => { form.reset(); form.classList.remove("was-validated"); $("step2").classList.add("d-none"); $("step1").classList.remove("d-none"); $("who").focus(); };
