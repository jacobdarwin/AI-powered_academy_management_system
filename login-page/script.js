// ===== Settings: change these for each academy =====
const ROLES = {
  superadmin: {
    label: "Super Admin",
    idLabel: "Email",
    idType: "email",
    idPlaceholder: "admin@youracademy.com",
    idError: "Enter a valid email address.",
    hint: "Full control of branches, users, fees and reports.",
    redirect: "superadmin/dashboard.html"
  },
  staff: {
    label: "Staff",
    idLabel: "Staff ID or email",
    idType: "text",
    idPlaceholder: "STF-0001 or name@youracademy.com",
    idError: "Enter your staff ID or email.",
    hint: "For trainers, counselors, placement officers and accounts.",
    redirect: "staff/dashboard.html"
  },
  student: {
    label: "Student",
    idLabel: "Student ID",
    idType: "text",
    idPlaceholder: "STU-2026-0001",
    idError: "Enter your student ID.",
    hint: "See your timetable, attendance, fees, marks and placement drives.",
    redirect: "student/dashboard.html"
  }
};

const form = document.getElementById("loginForm");
const userId = document.getElementById("userId");
const password = document.getElementById("password");
const alertBox = document.getElementById("formAlert");
const submitBtn = document.getElementById("submitBtn");
const spinner = document.getElementById("spinner");
let currentRole = "superadmin";

api.get("/settings/public").then(response => {
  if (response.data && response.data.academy_name) {
    document.getElementById("academyName").textContent = response.data.academy_name;
  }
}).catch(() => {});

// ---- Role switching ----
function setRole(role) {
  currentRole = role;
  const r = ROLES[role];

  document.querySelectorAll(".role-btn").forEach(btn => {
    const active = btn.dataset.role === role;
    btn.classList.toggle("active", active);
    btn.setAttribute("aria-selected", active);
  });

  document.getElementById("idLabel").textContent = r.idLabel;
  document.getElementById("idError").textContent = r.idError;
  document.getElementById("roleHint").textContent = r.hint;
  document.getElementById("submitText").textContent = "Sign in as " + r.label;
  userId.type = r.idType;
  userId.placeholder = r.idPlaceholder;

  form.reset();
  form.classList.remove("was-validated");
  alertBox.classList.add("d-none");
}

document.querySelectorAll(".role-btn").forEach(btn =>
  btn.addEventListener("click", () => setRole(btn.dataset.role))
);

// ---- Show / hide password ----
document.getElementById("togglePwd").addEventListener("click", function () {
  const show = password.type === "password";
  password.type = show ? "text" : "password";
  this.querySelector("i").className = show ? "bi bi-eye-slash" : "bi bi-eye";
  this.setAttribute("aria-label", show ? "Hide password" : "Show password");
});

// ---- Submit ----
form.addEventListener("submit", async (e) => {
  e.preventDefault();
  alertBox.classList.add("d-none");

  if (!form.checkValidity()) {
    form.classList.add("was-validated");
    return;
  }

  setLoading(true);
  try {
    const response = await api.post("/auth/login", {
      role: currentRole,
      userId: userId.value.trim(),
      password: password.value
    });
    const target = document.getElementById("remember").checked ? localStorage : sessionStorage;
    target.setItem("token", response.data.access_token);
    target.setItem("refresh_token", response.data.refresh_token);
    target.setItem("user", JSON.stringify(response.data.user));
    window.location.href = ROLES[currentRole].redirect;
  } catch (err) {
    alertBox.textContent = err.message || "We could not sign you in. Check your details and try again.";
    alertBox.classList.remove("d-none");
  } finally {
    setLoading(false);
  }
});

function setLoading(on) {
  submitBtn.disabled = on;
  spinner.classList.toggle("d-none", !on);
}

setRole("superadmin");
