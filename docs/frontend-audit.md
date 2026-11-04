# Frontend audit

## Scope and method

This audit covers all 45 HTML pages and all local JavaScript modules under
`login-page/`. The prototype is static HTML with Bootstrap 5, Bootstrap Icons,
Chart.js on chart pages, and shared layout builders. There are no live API
calls: the login and password-reset requests are commented examples, and
sample-data comments occur in 25 page modules. The existing page IDs and
rendering targets are the compatibility contract for backend integration.

All protected pages use one of three layout builders:

* `assets/admin.js`: superadmin shell and the full administration menu.
* `assets/staff.js`: staff shell; currently uses a demo role switcher and four
  hardcoded designations (Trainer, Counselor, Placement Officer, Accounts).
* `assets/student.js`: student shell and hardcoded student identity.

Every protected page also has a toast target (`toast`/`toastMsg`) except pages
whose module only renders a dashboard. Every list/table needs loading, empty,
error, filtering, and pagination states when connected to the API.

## Authentication pages

| Page | Role | Data displayed | Inputs and actions | Required API behavior |
|---|---|---|---|---|
| `index.html` | Public | Academy name, role tabs (Super Admin/Staff/Student), role-specific hint and validation text | `role`, `userId`, `password`, remember-me; show/hide password; submit; redirect by role | `POST /api/v1/auth/login`; `GET /api/v1/settings/public`; generic invalid-credentials response; store access/refresh tokens |
| `forgot-password.html` | Public | Academy name, two-step confirmation, submitted identifier | `who` (email/staff ID/student ID); send reset link; return to first step | `POST /api/v1/auth/forgot-password`; always return the same confirmation response |
| `reset-password.html` | Public, missing | New password and confirmation from a reset token | New password, confirm password, submit | Must be added; `POST /api/v1/auth/reset-password` |

## Superadmin pages

| Page | Data, filters, and actions | API resources |
|---|---|---|
| `superadmin/dashboard.html` | KPI cards for active students, running batches, fees collected/pending, placements; admissions and lead-funnel charts; recent admissions, upcoming drives, fee dues | `GET /dashboard/superadmin`; `GET /notifications/unread-count` for shell badge |
| `superadmin/leads.html` | Lead pipeline; search `q`; source and follow-up filters; lead rows; add/edit lead form: name, phone, course, source, counselor, follow-up date, note; save | `GET/POST/PATCH /leads`; `POST /leads/{id}/convert`; status/follow-up endpoints |
| `superadmin/students.html` | Student count/list; search; course/status/fee filters; CSV export; add/edit form: name, phone, email, DOB, course, batch, paid amount, parent, address; profile summary | `GET/POST/PATCH /students`; `GET /students/{id}/summary`; CSV export |
| `superadmin/courses.html` | Course cards and batch table; add course: name, fee, duration, tools; create batch: name/code, course, trainer, time, start date, seats | `GET/POST/PATCH /courses`; `GET/POST/PATCH /batches`; capacity and uniqueness validation |
| `superadmin/staff.html` | Staff directory; search and role filter; count; workload; add/edit form: name, phone, role/designation, joining date, salary, skills | `GET/POST/PATCH /staff`; `GET /staff/workload` |
| `superadmin/attendance.html` | Batch/date selector, roster statuses, summary and low-attendance list; mark all present; save bulk attendance | `GET /attendance`; `POST /attendance/bulk`; `GET /attendance/monthly-summary` |
| `superadmin/face.html` | Camera scan/enrollment, selected batch/student, consent, captured frames, recognized roster, save attendance/face data | Face enrollment/recognition endpoints; authenticated media upload; `POST /attendance/bulk` |
| `superadmin/fees.html` | Payment, pending-dues, and expense tabs; collect-fee form: student, balance, amount, mode; expense form: category, amount, note; receipt generation | `GET /payments`, `GET /fees/dues`, `POST /payments`, `GET /payments/{id}/receipt`; expense CRUD |
| `superadmin/placements.html` | Drives, placed students, companies; schedule drive form: title, company, role, date, package, eligible course, attendance threshold | Company/drive CRUD; placement summary; eligibility rules |
| `superadmin/applications.html` | Application pipeline; search student; company filter; export shortlisted; application rows and stage selector | `GET /applications`; `PATCH /applications/{id}`; CSV export |
| `superadmin/readiness.html` | Readiness chips, search, batch filter, readiness rows, CSV export | `GET /reports/placement-readiness` |
| `superadmin/notifications.html` | All/unread filter; notification list; mark all read | `GET /notifications/mine`; `POST /notifications/read-all`; unread count |
| `superadmin/reports.html` | Date-range selector; report KPIs/charts; print report | `GET /reports/admissions`, `/fees`, `/attendance`, `/placements`; printable/PDF response |
| `superadmin/settings.html` | Academy details form: name, phone, email, GST, address; fee settings: receipt prefix/grace/minimum; notification settings; password form; JSON backup | `GET/PATCH /settings`; `POST /auth/change-password`; backup/export endpoint |
| `superadmin/users.html` | User list/search/role filter; permissions matrix; add user form: name, email, role, password; generate password; save permissions | User CRUD, activation, password reset, role/permission endpoints |
| `superadmin/forecast.html` | Course selector, demand cards/chart, forecast table | `GET /reports/course-demand` |
| `superadmin/performance.html` | Staff-role filter, weights/bands, performance summary/table | `GET /reports/staff-performance` |

## Staff pages

Staff pages reuse the superadmin modules where noted, but the backend must
enforce designation permissions and object-level batch ownership rather than
trusting the current client-side menu.

| Page | Data, filters, and actions | API resources |
|---|---|---|
| `staff/dashboard.html` | Greeting/date; workload KPIs; today's classes; action links; pending items | `GET /dashboard/staff` |
| `staff/batches.html` | Assigned batch cards; batch roster modal | `GET /staff/me/batches`; `GET /batches/{id}/students` |
| `staff/attendance.html` | Same batch/date roster workflow as superadmin | `GET /attendance`; `POST /attendance/bulk` scoped to assigned batches |
| `staff/face.html` | Same camera scan/enrollment workflow as superadmin | Face endpoints scoped to assigned batches |
| `staff/marks.html` | Batch/test selectors, max marks, roster marks, summary; save marks | Assessment CRUD; `POST /marks/bulk` scoped to assigned batches |
| `staff/materials.html` | Upload form: title, type, batch, file; material list/delete/empty state | `POST /materials` multipart; `GET/DELETE /materials`; authenticated download |
| `staff/leads.html` | Same lead pipeline and lead form as superadmin, subject to counselor permissions | Leads CRUD/status/follow-up |
| `staff/students.html` | Same student list/add/profile/export as superadmin, scoped by designation/batch | Students CRUD/summary/export |
| `staff/fees.html` | Same payments/dues/expenses UI as superadmin, subject to accounts permission | Fees/payments/expenses |
| `staff/placements.html` | Same drives/placed/company UI as superadmin, subject to placement-officer permission | Companies/drives/applications |
| `staff/applications.html` | Same applications pipeline/search/company filter/export | Applications |
| `staff/readiness.html` | Same readiness search/batch filter/export | Placement-readiness report |
| `staff/profile.html` | Profile form: name/phone/email; password form | `GET/PATCH /staff/me`; `POST /auth/change-password` |
| `staff/notifications.html` | All/unread notifications; mark all read | Notifications |

## Student pages

Student endpoints must derive the student identity from the JWT. No request
parameter may allow a student to read another student’s records.

| Page | Data, filters, and actions | API resources |
|---|---|---|
| `student/dashboard.html` | Greeting, course/progress, attendance/fee/marks KPIs, classes, deadlines, drives, news | `GET /dashboard/student` |
| `student/timetable.html` | Week navigation and timetable grid | `GET /me/timetable` |
| `student/attendance.html` | Attendance percentage/warning, month navigation, calendar | `GET /me/attendance`; monthly summary |
| `student/fees.html` | Fee KPIs, installments, payment history; placeholder Pay online button | `GET /me/fees`; `GET /me/payments`; payment gateway is not yet specified |
| `student/marks.html` | Test/assignment tabs; average and assessment history | `GET /me/marks`; `GET /me/assessments` |
| `student/materials.html` | Search and type filter; materials list/download/empty state | `GET /me/materials`; authenticated download |
| `student/placements.html` | Attendance/readiness indicator; resume upload/name; open drives and own applications | `GET /placements/open`; `POST /applications`; `GET /me/applications`; resume upload |
| `student/readiness.html` | Readiness gauge, score/category/explanation, factors, tips; mock interview action | `GET /me/readiness`; mock-interview booking endpoint |
| `student/certificates.html` | Eligibility/final result and certificate list/download | `GET /me/certificates`; eligibility and PDF download |
| `student/notifications.html` | All/unread notifications; mark all read | Notifications |
| `student/profile.html` | Profile/photo and fixed identity fields; editable phone/email/parent/address; password form | `GET/PATCH /me/profile`; photo upload; `POST /auth/change-password` |
| `student/assistant.html` | Chat history, quick chips, prompt input, response stream/list | Assistant endpoint is not defined in the prompt; see open questions |

## Shared modules and cross-cutting observations

* `assets/js/applications.js`: shared application list, company filter,
  pipeline counts, stage changes, and shortlist export.
* `assets/js/notifications.js`: shared list, all/unread filter, mark-read and
  mark-all-read.
* `assets/js/face.js`: camera permissions, face capture, recognition result,
  enrollment consent, and attendance save.
* `assets/js/readiness.js`: shared readiness list/search/batch filter/export.
* `assets/js/superadmin/*`: administration dashboards, CRUD, reports, fees,
  attendance, leads, placements, settings, staff, students, users.
* `assets/js/staff/*`: assigned batches, dashboard, marks, materials, profile.
* `assets/js/student/*`: dashboard, attendance, certificates, fees, marks,
  materials, placements, profile, readiness, timetable, assistant.

The current HTML uses template strings in several renderers. Integration must
add one shared `escapeHtml()` helper and apply it to every API-originated value
before assigning `innerHTML`. `api.js` must also provide loading/error/empty
helpers or consistent page-level equivalents.

## Schema reconciliation

The proposed schema covers the core UI entities: users, staff, students,
courses, batches, leads, attendance, fees/payments, marks/assessments,
materials, companies/drives/applications, certificates, notifications,
settings, and audit logs. The audit requires these additions or clarifications:

1. `assessments` and `marks` need an `assessment_type`/assignment distinction,
   maximum marks, date, and optional submission/feedback fields for the marks
   tabs.
2. `expenses` and `expense_categories` are required by both fee pages.
3. `companies` and placement drives need role, package, date, eligible course,
   attendance threshold, status, and offer details.
4. `staff` needs salary/skills if those fields remain in the staff modal.
5. Student profile needs an avatar/photo upload and resume path.
6. Face attendance needs consent, enrollment metadata, and face-vector storage
   handled by a dedicated service; raw biometric data must not be exposed.
7. `assistant` conversations/messages and mock-interview bookings are not in
   the schema and need a product decision before implementation.
8. Course demand forecast and staff performance weights/bands need persisted
   configuration or explicitly computed report contracts.
9. The UI has `GST` and backup settings fields; add them to settings if they
   are supported, otherwise remove them from the contract.
10. The frontend currently has no reset-password page; it must be added before
    the reset-token API can be used.

## Open questions before implementation

1. Should the assistant be a real external/LLM-backed feature, a local FAQ
   service, or remain disabled in the backend phase?
2. Which payment gateway, if any, should power the student **Pay online**
   button? Until selected, it should remain disabled with an explicit
   “coming soon” state.
3. What face-recognition provider and retention policy are approved? Browser
   camera capture alone is not identity verification.
4. Should “Branch Manager” from the users permission UI map to `superadmin`,
   become a separate role, or be removed?
5. Are salary, GST, expense, forecast, performance, mock interviews, and
   backups required in the first production release?
6. What SMTP provider and sender address should be used for reset links?
7. Should the backend serve this existing `login-page/` directory directly, or
   should it be copied/renamed to the prompt’s `frontend/` directory?
