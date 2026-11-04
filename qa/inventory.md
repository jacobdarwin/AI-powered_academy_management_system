# Stage 0 QA Inventory

Generated from the live Flask URL map, SQLAlchemy metadata, source decorators, and frontend JavaScript scans on 2026-11-03.

## Baseline

- Command: `py -m pytest -q --cov=app --cov-report=term-missing`
- Result: **27 passed in 20.04s**
- Overall `app` coverage: **62%** (2126 statements, 812 missed)
- `app/services` package: **not present** in the repository.

## Registered routes

| Methods | Path | Endpoint | Decorator evidence |
| --- | --- | --- | --- |
| GET | / | frontend_index | none found |
| GET | /<path:filename> | frontend_file | none found |
| GET, POST | /api/v1/applications | api.placements.applications | placements_api.route('/applications', methods=['GET', 'POST']), authenticated |
| PATCH | /api/v1/applications/<int:application_id> | api.placements.update_application | _placement_staff |
| POST | /api/v1/assessments | api.academics.create_assessment | roles_required('superadmin', 'staff') |
| GET | /api/v1/attendance | api.academics.list_attendance | roles_required('superadmin', 'staff') |
| POST | /api/v1/attendance/bulk | api.academics.bulk_attendance | roles_required('superadmin', 'staff') |
| GET | /api/v1/attendance/monthly-summary | api.academics.monthly_summary | roles_required('superadmin', 'staff') |
| POST | /api/v1/auth/change-password | api.auth.change_password | authenticated |
| POST | /api/v1/auth/forgot-password | api.auth.forgot_password | none found |
| POST | /api/v1/auth/login | api.auth.login | none found |
| POST | /api/v1/auth/logout | api.auth.logout | none found |
| GET | /api/v1/auth/me | api.auth.me | authenticated |
| POST | /api/v1/auth/refresh | api.auth.refresh | none found |
| POST | /api/v1/auth/reset-password | api.auth.reset_password | none found |
| GET | /api/v1/batches | api.resources.list_batches | authenticated |
| POST | /api/v1/batches | api.resources.create_batch | roles_required('superadmin') |
| DELETE | /api/v1/batches/<int:batch_id> | api.resources.delete_batch | roles_required('superadmin') |
| PATCH | /api/v1/batches/<int:batch_id> | api.resources.update_batch | roles_required('superadmin') |
| POST | /api/v1/certificates | api.placements.issue_certificate | _placement_staff |
| GET | /api/v1/certificates/<int:certificate_id>/download | api.placements.download_certificate | authenticated |
| GET | /api/v1/certificates/eligibility | api.placements.certificate_eligibility | authenticated |
| GET, POST | /api/v1/companies | api.placements.companies | placements_api.route('/companies', methods=['GET', 'POST']), _placement_staff |
| GET, PATCH | /api/v1/companies/<int:company_id> | api.placements.company | placements_api.route('/companies/<int:company_id>', methods=['GET', 'PATCH']), _placement_staff |
| GET | /api/v1/courses | api.resources.list_courses | authenticated |
| POST | /api/v1/courses | api.resources.create_course | roles_required('superadmin') |
| DELETE | /api/v1/courses/<int:course_id> | api.resources.delete_course | roles_required('superadmin') |
| PATCH | /api/v1/courses/<int:course_id> | api.resources.update_course | roles_required('superadmin') |
| GET | /api/v1/dashboard | api.phase8.dashboard | authenticated |
| GET | /api/v1/dashboard/<role> | api.phase8.role_dashboard | authenticated |
| GET | /api/v1/dashboard/superadmin | api.phase8.superadmin_dashboard | roles_required('superadmin') |
| GET, POST | /api/v1/drives | api.placements.drives | placements_api.route('/drives', methods=['GET', 'POST']), _placement_staff |
| GET, PATCH | /api/v1/drives/<int:drive_id> | api.placements.drive | placements_api.route('/drives/<int:drive_id>', methods=['GET', 'PATCH']), _placement_staff |
| GET | /api/v1/fees/dues | api.fees.dues | roles_required('superadmin', 'staff') |
| GET, POST | /api/v1/fees/expenses | api.fees.expenses | fees_api.route('/expenses', methods=['GET', 'POST']), roles_required('superadmin', 'staff') |
| PATCH | /api/v1/fees/expenses/<int:expense_id> | api.fees.update_expense | roles_required('superadmin', 'staff') |
| GET | /api/v1/fees/me | api.fees.my_fees | roles_required('student') |
| GET | /api/v1/fees/payments | api.fees.list_payments | roles_required('superadmin', 'staff') |
| POST | /api/v1/fees/payments | api.fees.create_payment | roles_required('superadmin', 'staff') |
| GET | /api/v1/fees/payments/<int:payment_id>/receipt | api.fees.payment_receipt | authenticated |
| POST | /api/v1/fees/payments/<int:payment_id>/void | api.fees.void_payment | roles_required('superadmin', 'staff') |
| GET | /api/v1/fees/plans | api.fees.list_plans | roles_required('superadmin', 'staff') |
| POST | /api/v1/fees/plans | api.fees.create_plan | roles_required('superadmin', 'staff') |
| GET | /api/v1/health | api.health | none found |
| GET | /api/v1/leads | api.leads.list_leads | roles_required('superadmin', 'staff') |
| POST | /api/v1/leads | api.leads.create_lead | roles_required('superadmin', 'staff') |
| GET | /api/v1/leads/<int:lead_id> | api.leads.get_lead | roles_required('superadmin', 'staff') |
| PATCH | /api/v1/leads/<int:lead_id> | api.leads.update_lead | roles_required('superadmin', 'staff') |
| POST | /api/v1/leads/<int:lead_id>/convert | api.leads.convert_lead | roles_required('superadmin', 'staff') |
| POST | /api/v1/leads/<int:lead_id>/follow-ups | api.leads.add_follow_up | roles_required('superadmin', 'staff') |
| PATCH | /api/v1/leads/<int:lead_id>/status | api.leads.update_status | roles_required('superadmin', 'staff') |
| GET | /api/v1/marks | api.academics.list_marks | authenticated |
| POST | /api/v1/marks/bulk | api.academics.bulk_marks | roles_required('superadmin', 'staff') |
| GET | /api/v1/materials | api.phase8.list_materials | authenticated |
| POST | /api/v1/materials | api.phase8.upload_material | roles_required('superadmin', 'staff') |
| DELETE | /api/v1/materials/<int:material_id> | api.phase8.delete_material | roles_required('superadmin', 'staff') |
| GET | /api/v1/materials/<int:material_id>/download | api.phase8.download_material | authenticated |
| POST | /api/v1/materials/upload | api.phase8.upload_material | roles_required('superadmin', 'staff') |
| GET | /api/v1/me/applications | api.placements.my_applications | authenticated |
| GET | /api/v1/me/assessments | api.academics.my_assessments | roles_required('student') |
| GET | /api/v1/me/certificates | api.placements.my_certificates | authenticated |
| GET | /api/v1/me/marks | api.academics.my_marks | roles_required('student') |
| GET | /api/v1/notifications | api.phase8.list_notifications | authenticated |
| POST | /api/v1/notifications | api.phase8.create_notification | roles_required('superadmin', 'staff') |
| POST | /api/v1/notifications/<int:notification_id>/read | api.phase8.mark_notification_read | authenticated |
| GET | /api/v1/notifications/mine | api.phase8.list_my_notifications | authenticated |
| POST | /api/v1/notifications/read-all | api.phase8.mark_all_notifications_read | authenticated |
| GET | /api/v1/notifications/unread | api.phase8.unread_notifications | authenticated |
| GET | /api/v1/placements/open | api.placements.open_drives | authenticated |
| GET | /api/v1/protected/staff-check | api.protected.staff_check | roles_required('staff') |
| GET | /api/v1/protected/superadmin-check | api.protected.superadmin_check | roles_required('superadmin') |
| GET | /api/v1/reports/admissions | api.phase8.admissions_report | roles_required('superadmin') |
| GET | /api/v1/reports/attendance | api.phase8.attendance_report | roles_required('superadmin', 'staff') |
| GET | /api/v1/reports/fees | api.phase8.fees_report | roles_required('superadmin', 'staff') |
| GET | /api/v1/settings | api.phase8.get_settings | roles_required('superadmin') |
| PATCH | /api/v1/settings | api.phase8.update_settings | roles_required('superadmin') |
| PUT | /api/v1/settings | api.phase8.update_settings | roles_required('superadmin') |
| GET | /api/v1/settings/backup | api.phase8.settings_backup | roles_required('superadmin') |
| GET | /api/v1/settings/public | api.phase8.public_settings | none found |
| GET | /api/v1/staff | api.resources.list_staff | roles_required('superadmin') |
| POST | /api/v1/staff | api.resources.create_staff | roles_required('superadmin') |
| DELETE | /api/v1/staff/<int:staff_id> | api.resources.delete_staff | roles_required('superadmin') |
| PATCH | /api/v1/staff/<int:staff_id> | api.resources.update_staff | roles_required('superadmin') |
| GET | /api/v1/staff/workload | api.resources.staff_workload | roles_required('superadmin') |
| GET | /api/v1/students | api.resources.list_students | authenticated |
| POST | /api/v1/students | api.resources.create_student | roles_required('superadmin', 'staff') |
| GET | /api/v1/students/<int:student_id> | api.resources.get_student | authenticated |
| PATCH | /api/v1/students/<int:student_id> | api.resources.update_student | authenticated |
| GET | /api/v1/students/<int:student_id>/attendance | api.academics.student_attendance | authenticated |
| GET | /api/v1/students/export | api.resources.export_students | roles_required('superadmin', 'staff') |
| GET | /api/v1/users | api.resources.list_users | roles_required('superadmin') |
| POST | /api/v1/users | api.resources.create_user | roles_required('superadmin') |
| GET | /api/v1/users/<int:user_id> | api.resources.get_user | roles_required('superadmin') |
| PATCH | /api/v1/users/<int:user_id> | api.resources.update_user | roles_required('superadmin') |
| POST | /api/v1/users/<int:user_id>/activate | api.resources.activate_user | roles_required('superadmin') |
| POST | /api/v1/users/<int:user_id>/deactivate | api.resources.deactivate_user | roles_required('superadmin') |
| POST | /api/v1/users/<int:user_id>/reset-password | api.resources.reset_user_password | roles_required('superadmin') |
| GET | /static/<path:filename> | static | none found |

## Models and tables

| Table | Columns | Constraints/indexes |
| --- | --- | --- |
| applications | `id` INTEGER [PK, NOT NULL]; `drive_id` INTEGER [NOT NULL]; `student_id` INTEGER [NOT NULL]; `stage` VARCHAR(32) [NOT NULL]; `offer_details` JSON; `created_at` DATETIME [NOT NULL]; `updated_at` DATETIME [NOT NULL] | UNIQUE(drive_id, student_id); FK(student_id); FK(drive_id); ix_applications_student_id(student_id); ix_applications_drive_id(drive_id) |
| assessments | `id` INTEGER [PK, NOT NULL]; `batch_id` INTEGER [NOT NULL]; `title` VARCHAR(160) [NOT NULL]; `assessment_type` VARCHAR(32) [NOT NULL]; `max_marks` NUMERIC(8, 2) [NOT NULL]; `date` DATE [NOT NULL]; `created_at` DATETIME [NOT NULL]; `updated_at` DATETIME [NOT NULL] | FK(batch_id); ix_assessments_batch_id(batch_id) |
| attendance | `id` INTEGER [PK, NOT NULL]; `student_id` INTEGER [NOT NULL]; `batch_id` INTEGER [NOT NULL]; `date` DATE [NOT NULL]; `status` VARCHAR(16) [NOT NULL]; `note` TEXT; `created_at` DATETIME [NOT NULL]; `updated_at` DATETIME [NOT NULL] | FK(student_id); UNIQUE(student_id, date); FK(batch_id); ix_attendance_date(date); ix_attendance_batch_id(batch_id); ix_attendance_student_id(student_id) |
| audit_logs | `id` INTEGER [PK, NOT NULL]; `user_id` INTEGER; `action` VARCHAR(64) [NOT NULL]; `entity` VARCHAR(64) [NOT NULL]; `entity_id` INTEGER; `before` JSON; `after` JSON; `ip` VARCHAR(64); `created_at` DATETIME [NOT NULL] | FK(user_id); ix_audit_logs_user_id(user_id) |
| batches | `id` INTEGER [PK, NOT NULL]; `code` VARCHAR(64) [UNIQUE, NOT NULL]; `course_id` INTEGER [NOT NULL]; `trainer_id` INTEGER; `schedule` VARCHAR(255); `start_date` DATE; `end_date` DATE; `capacity` INTEGER [NOT NULL]; `status` VARCHAR(32) [NOT NULL]; `created_at` DATETIME [NOT NULL]; `updated_at` DATETIME [NOT NULL] | FK(trainer_id); FK(course_id); ix_batches_course_id(course_id); ix_batches_code(code); ix_batches_trainer_id(trainer_id) |
| certificates | `id` INTEGER [PK, NOT NULL]; `student_id` INTEGER [NOT NULL]; `certificate_no` VARCHAR(64) [UNIQUE, NOT NULL]; `issued_on` DATE [NOT NULL]; `file_path` VARCHAR(512); `created_at` DATETIME [NOT NULL]; `updated_at` DATETIME [NOT NULL] | FK(student_id); UNIQUE(certificate_no); ix_certificates_student_id(student_id) |
| companies | `id` INTEGER [PK, NOT NULL]; `name` VARCHAR(160) [UNIQUE, NOT NULL]; `website` VARCHAR(255); `contact` VARCHAR(255); `created_at` DATETIME [NOT NULL]; `updated_at` DATETIME [NOT NULL] | UNIQUE(name) |
| courses | `id` INTEGER [PK, NOT NULL]; `name` VARCHAR(160) [NOT NULL]; `code` VARCHAR(32) [UNIQUE, NOT NULL]; `duration_months` INTEGER [NOT NULL]; `total_fee` NUMERIC(10, 2) [NOT NULL]; `description` TEXT; `is_active` BOOLEAN [NOT NULL]; `created_at` DATETIME [NOT NULL]; `updated_at` DATETIME [NOT NULL]; `is_deleted` BOOLEAN [NOT NULL]; `deleted_at` DATETIME | ix_courses_is_deleted(is_deleted); ix_courses_code(code) |
| expenses | `id` INTEGER [PK, NOT NULL]; `category` VARCHAR(128) [NOT NULL]; `amount` NUMERIC(10, 2) [NOT NULL]; `note` TEXT; `date` DATE [NOT NULL]; `created_by` INTEGER [NOT NULL]; `created_at` DATETIME [NOT NULL]; `updated_at` DATETIME [NOT NULL] | FK(created_by); ix_expenses_date(date) |
| face_enrollments | `id` INTEGER [PK, NOT NULL]; `student_id` INTEGER [UNIQUE, NOT NULL]; `consented_at` DATETIME [NOT NULL]; `vector_reference` VARCHAR(512) [NOT NULL]; `is_active` BOOLEAN [NOT NULL]; `created_at` DATETIME [NOT NULL]; `updated_at` DATETIME [NOT NULL] | FK(student_id); UNIQUE(student_id) |
| fee_plans | `id` INTEGER [PK, NOT NULL]; `student_id` INTEGER [NOT NULL]; `final_amount` NUMERIC(10, 2) [NOT NULL]; `status` VARCHAR(32) [NOT NULL]; `created_at` DATETIME [NOT NULL]; `updated_at` DATETIME [NOT NULL] | FK(student_id); ix_fee_plans_student_id(student_id) |
| installments | `id` INTEGER [PK, NOT NULL]; `fee_plan_id` INTEGER [NOT NULL]; `label` VARCHAR(128) [NOT NULL]; `due_date` DATE [NOT NULL]; `amount` NUMERIC(10, 2) [NOT NULL]; `paid_amount` NUMERIC(10, 2) [NOT NULL]; `status` VARCHAR(32) [NOT NULL]; `created_at` DATETIME [NOT NULL]; `updated_at` DATETIME [NOT NULL] | FK(fee_plan_id); ix_installments_fee_plan_id(fee_plan_id); ix_installments_due_date(due_date) |
| lead_follow_ups | `id` INTEGER [PK, NOT NULL]; `lead_id` INTEGER [NOT NULL]; `staff_id` INTEGER; `follow_up_on` DATE [NOT NULL]; `note` TEXT [NOT NULL]; `status` VARCHAR(32) [NOT NULL]; `created_at` DATETIME [NOT NULL]; `updated_at` DATETIME [NOT NULL] | FK(lead_id); FK(staff_id); ix_lead_follow_ups_staff_id(staff_id); ix_lead_follow_ups_lead_id(lead_id) |
| leads | `id` INTEGER [PK, NOT NULL]; `name` VARCHAR(160) [NOT NULL]; `phone` VARCHAR(32) [NOT NULL]; `email` VARCHAR(255); `course_id` INTEGER; `source` VARCHAR(64); `counselor_id` INTEGER; `follow_up_on` DATE; `note` TEXT; `status` VARCHAR(32) [NOT NULL]; `converted_student_id` INTEGER; `created_at` DATETIME [NOT NULL]; `updated_at` DATETIME [NOT NULL]; `is_deleted` BOOLEAN [NOT NULL]; `deleted_at` DATETIME | FK(counselor_id); FK(course_id); FK(converted_student_id); ix_leads_course_id(course_id); ix_leads_phone(phone); ix_leads_counselor_id(counselor_id); ix_leads_is_deleted(is_deleted); ix_leads_status(status) |
| marks | `id` INTEGER [PK, NOT NULL]; `assessment_id` INTEGER [NOT NULL]; `student_id` INTEGER [NOT NULL]; `marks_obtained` NUMERIC(8, 2) [NOT NULL]; `feedback` TEXT; `created_at` DATETIME [NOT NULL]; `updated_at` DATETIME [NOT NULL] | FK(student_id); FK(assessment_id); UNIQUE(assessment_id, student_id); ix_marks_student_id(student_id); ix_marks_assessment_id(assessment_id) |
| materials | `id` INTEGER [PK, NOT NULL]; `batch_id` INTEGER [NOT NULL]; `uploaded_by` INTEGER [NOT NULL]; `title` VARCHAR(255) [NOT NULL]; `material_type` VARCHAR(32) [NOT NULL]; `file_path` VARCHAR(512) [NOT NULL]; `file_size` INTEGER; `created_at` DATETIME [NOT NULL]; `updated_at` DATETIME [NOT NULL] | FK(uploaded_by); FK(batch_id); ix_materials_batch_id(batch_id) |
| notification_reads | `notification_id` INTEGER [PK, NOT NULL]; `user_id` INTEGER [PK, NOT NULL]; `read_at` DATETIME [NOT NULL] | FK(notification_id); FK(user_id) |
| notifications | `id` INTEGER [PK, NOT NULL]; `title` VARCHAR(255) [NOT NULL]; `message` TEXT [NOT NULL]; `audience` VARCHAR(32) [NOT NULL]; `audience_ref_id` INTEGER; `created_by` INTEGER [NOT NULL]; `created_at` DATETIME [NOT NULL]; `updated_at` DATETIME [NOT NULL] | FK(created_by); ix_notifications_audience(audience) |
| password_reset_tokens | `id` INTEGER [PK, NOT NULL]; `user_id` INTEGER [NOT NULL]; `token_hash` VARCHAR(128) [UNIQUE, NOT NULL]; `expires_at` DATETIME [NOT NULL]; `used_at` DATETIME; `created_at` DATETIME [NOT NULL]; `updated_at` DATETIME [NOT NULL] | UNIQUE(token_hash); FK(user_id); ix_password_reset_tokens_user_id(user_id) |
| payments | `id` INTEGER [PK, NOT NULL]; `student_id` INTEGER [NOT NULL]; `installment_id` INTEGER; `receipt_no` VARCHAR(64) [UNIQUE, NOT NULL]; `amount` NUMERIC(10, 2) [NOT NULL]; `mode` VARCHAR(32) [NOT NULL]; `reference` VARCHAR(128); `status` VARCHAR(16) [NOT NULL]; `void_reason` TEXT; `created_at` DATETIME [NOT NULL]; `updated_at` DATETIME [NOT NULL] | FK(student_id); FK(installment_id); ix_payments_installment_id(installment_id); ix_payments_student_id(student_id); ix_payments_receipt_no(receipt_no) |
| placement_drives | `id` INTEGER [PK, NOT NULL]; `company_id` INTEGER [NOT NULL]; `title` VARCHAR(160) [NOT NULL]; `role` VARCHAR(160) [NOT NULL]; `drive_date` DATE [NOT NULL]; `package` NUMERIC(10, 2); `course_id` INTEGER; `attendance_threshold` NUMERIC(5, 2); `marks_threshold` NUMERIC(5, 2); `status` VARCHAR(32) [NOT NULL]; `created_at` DATETIME [NOT NULL]; `updated_at` DATETIME [NOT NULL] | FK(course_id); FK(company_id); ix_placement_drives_company_id(company_id); ix_placement_drives_course_id(course_id); ix_placement_drives_status(status) |
| receipt_sequences | `id` INTEGER [PK, NOT NULL]; `prefix` VARCHAR(32) [UNIQUE, NOT NULL]; `next_number` INTEGER [NOT NULL] | UNIQUE(prefix) |
| revoked_tokens | `id` INTEGER [PK, NOT NULL]; `jti` VARCHAR(64) [UNIQUE, NOT NULL]; `revoked_at` DATETIME [NOT NULL] | ix_revoked_tokens_jti(jti) |
| settings | `id` INTEGER [PK, NOT NULL]; `key` VARCHAR(128) [UNIQUE, NOT NULL]; `value` JSON [NOT NULL]; `created_at` DATETIME [NOT NULL]; `updated_at` DATETIME [NOT NULL] | UNIQUE(key) |
| staff | `id` INTEGER [PK, NOT NULL]; `user_id` INTEGER [UNIQUE, NOT NULL]; `staff_code` VARCHAR(32) [UNIQUE, NOT NULL]; `name` VARCHAR(160) [NOT NULL]; `phone` VARCHAR(32); `designation` VARCHAR(32) [NOT NULL]; `qualification` VARCHAR(255); `joined_on` DATE; `salary` NUMERIC(10, 2); `skills` TEXT; `status` VARCHAR(32) [NOT NULL]; `photo_path` VARCHAR(512); `created_at` DATETIME [NOT NULL]; `updated_at` DATETIME [NOT NULL]; `is_deleted` BOOLEAN [NOT NULL]; `deleted_at` DATETIME | FK(user_id); UNIQUE(user_id); ix_staff_is_deleted(is_deleted); ix_staff_designation(designation); ix_staff_staff_code(staff_code) |
| students | `id` INTEGER [PK, NOT NULL]; `user_id` INTEGER [UNIQUE, NOT NULL]; `student_code` VARCHAR(32) [UNIQUE, NOT NULL]; `name` VARCHAR(160) [NOT NULL]; `email` VARCHAR(255); `phone` VARCHAR(32); `dob` DATE; `gender` VARCHAR(32); `address` TEXT; `guardian_name` VARCHAR(160); `guardian_phone` VARCHAR(32); `qualification` VARCHAR(255); `college` VARCHAR(255); `year_of_passing` INTEGER; `course_id` INTEGER; `batch_id` INTEGER; `admission_date` DATE; `status` VARCHAR(32) [NOT NULL]; `lead_id` INTEGER; `photo_path` VARCHAR(512); `resume_path` VARCHAR(512); `placed_status` VARCHAR(32) [NOT NULL]; `created_at` DATETIME [NOT NULL]; `updated_at` DATETIME [NOT NULL]; `is_deleted` BOOLEAN [NOT NULL]; `deleted_at` DATETIME | FK(batch_id); FK(lead_id); FK(user_id); FK(course_id); UNIQUE(user_id); ix_students_batch_id(batch_id); ix_students_status(status); ix_students_course_id(course_id); ix_students_student_code(student_code); ix_students_is_deleted(is_deleted) |
| users | `id` INTEGER [PK, NOT NULL]; `email` VARCHAR(255) [UNIQUE]; `login_id` VARCHAR(64) [UNIQUE, NOT NULL]; `password_hash` VARCHAR(255) [NOT NULL]; `role` VARCHAR(32) [NOT NULL]; `is_active` BOOLEAN [NOT NULL]; `must_change_password` BOOLEAN [NOT NULL]; `last_login_at` DATETIME; `failed_login_count` INTEGER [NOT NULL]; `locked_until` DATETIME; `created_at` DATETIME [NOT NULL]; `updated_at` DATETIME [NOT NULL] | ix_users_role(role); ix_users_email(email); ix_users_login_id(login_id) |

## Frontend pages

| HTML page |
| --- |
| forgot-password.html |
| index.html |
| reset-password.html |
| staff/applications.html |
| staff/attendance.html |
| staff/batches.html |
| staff/dashboard.html |
| staff/face.html |
| staff/fees.html |
| staff/leads.html |
| staff/marks.html |
| staff/materials.html |
| staff/notifications.html |
| staff/placements.html |
| staff/profile.html |
| staff/readiness.html |
| staff/students.html |
| student/assistant.html |
| student/attendance.html |
| student/certificates.html |
| student/dashboard.html |
| student/fees.html |
| student/marks.html |
| student/materials.html |
| student/notifications.html |
| student/placements.html |
| student/profile.html |
| student/readiness.html |
| student/timetable.html |
| superadmin/applications.html |
| superadmin/attendance.html |
| superadmin/courses.html |
| superadmin/dashboard.html |
| superadmin/face.html |
| superadmin/fees.html |
| superadmin/forecast.html |
| superadmin/leads.html |
| superadmin/notifications.html |
| superadmin/performance.html |
| superadmin/placements.html |
| superadmin/readiness.html |
| superadmin/reports.html |
| superadmin/settings.html |
| superadmin/staff.html |
| superadmin/students.html |
| superadmin/users.html |

## Frontend API calls

| JavaScript file | Calls found |
| --- | --- |
| assets/js/applications.js | api.get("/applications?per_page=100"),<br>api.get("/students?per_page=100"),<br>api.get("/drives?per_page=100"),<br>api.get("/companies?per_page=100")<br>api.patch(`/applications/${id}`, {status}); await load(); saToast("Application updated."); } |
| assets/js/forgot-password.js | api.post("/auth/forgot-password", { identifier: $("who").value.trim() }) |
| assets/js/notifications.js | api.get("/notifications/mine")<br>api.post(`/notifications/${id}/read`); await refresh(); }<br>api.post("/notifications/read-all"); await refresh(); } |
| assets/js/staff/batches.js | api.get(`/batches/${batch.id}/students?per_page=100`)<br>api.get("/staff/me/batches") |
| assets/js/staff/dashboard.js | api.get("/dashboard/staff") |
| assets/js/staff/marks.js | api.get(`/batches/${$("batch").value}/students?per_page=100`)<br>api.post("/assessments", {batch_id: Number($("batch").value), title: $("test").value.trim(), type: "test", assessment_type: "test", max_marks: Number($("max").value), date: new Date().toISOString().slice(0, 10)})<br>api.post("/marks/bulk", {assessment_id: assessment.data.id, records: Object.entries(marks).filter(([, value]) => value !== "").map(([student_id, value]) => ({student_id: Number(student_id), marks: Number(value)}))})<br>api.get("/staff/me/batches").then(response => { |
| assets/js/staff/materials.js | api.delete(`/materials/${id}`); items = items.filter(item => item.id !== id); render(); toast("Material deleted."); }<br>api.upload("/materials", body); form.reset(); form.classList.remove("was-validated"); await load(); toast("Material uploaded.")<br>api.get("/materials"), api.get("/staff/me/batches")]) |
| assets/js/staff/profile.js | api.get("/staff/me")).data \|\| {}<br>api.patch("/staff/me", {name: $("who").value.split(" (")[0], phone: $("phone").value.trim(), email: $("email").value.trim()}); toast("Profile saved."); }<br>api.post("/auth/change-password", {current_password: $("p0").value, new_password: $("p1").value}); form.reset(); form.classList.remove("was-validated"); toast("Password updated."); } |
| assets/js/student/assistant.js | api.post("/assistant/messages", {message: clean}); pending.textContent = response.data?.message \|\| response.data?.reply \|\| "No response."; } catch (error) { pending.textContent = error.message \|\| "Assistant unavailable."; saError(error); } } |
| assets/js/student/attendance.js | api.get("/students?per_page=1")).data[0]; const response = await api.get(`/students/${student.id}/attendance`); records = response.data.records \|\| []; render(); } catch (error) { saError(error); saEmpty("cal", "Unable to load attendance."); saEmpty("stats", "Unable to load attendance."); } } |
| assets/js/student/certificates.js | api.get(`/certificates/${id}/download`); const link = document.createElement("a"); link.href = URL.createObjectURL(new Blob([response.data], {type: "application/pdf"})); link.download = "certificate.pdf"; link.click(); URL.revokeObjectURL(link.href); } catch (error) { saError(error); } }<br>api.get("/certificates/eligibility"), api.get("/me/certificates")]).then(result => { certificates = result[1].data \|\| []; render(result[0].data \|\| {}); }).catch(error => { saError(error); saEmpty("final", "Unable to load certificate eligibility."); saEmpty("list", "Unable to load certificates."); }) |
| assets/js/student/dashboard.js | api.get("/dashboard/student").then(response => render(response.data \|\| {})).catch(error => { saError(error); ["stats", "classes", "deadlines", "drives", "news"].forEach(id => saEmpty(id, "Unable to load dashboard.")); }) |
| assets/js/student/fees.js | api.get(`/payments/${id}/receipt?format=json`); const item = response.data; const win = window.open("", "_blank", "width=520,height=600"); win.document.write(`<body style="font-family:sans-serif;padding:32px"><h2>${saEscape("Academy")}</h2><p>Receipt: ${saEscape(item.receipt_no)}</p><p>Amount: ${saEscape(money(item.amount))}</p></body>`); win.document.close(); win.print(); } catch (error) { saError(error); } }<br>api.get("/me/fees"), api.get("/me/payments")]).then(result => { history = result[1].data \|\| []; render(result[0].data \|\| {}); }).catch(error => { saError(error); ["stats", "inst", "hist"].forEach(id => saEmpty(id, "Unable to load fees.")); }) |
| assets/js/student/marks.js | api.get("/me/marks"), api.get("/me/assessments")]).then(result => render(result[0].data \|\| [], result[1].data \|\| [])).catch(error => { saError(error); ["stats", "tests", "asg"].forEach(id => saEmpty(id, "Unable to load marks.")); }) |
| assets/js/student/materials.js | api.get(`/materials/${id}/download`); const link = document.createElement("a"); link.href = URL.createObjectURL(new Blob([response.data])); link.download = "material"; link.click(); URL.revokeObjectURL(link.href); } catch (error) { saError(error); } }<br>api.get("/me/materials").then(response => { items = response.data \|\| []; render(); }).catch(error => { saError(error); saEmpty("list", "Unable to load materials."); }) |
| assets/js/student/placements.js | api.post("/applications", {drive_id: drives[index].id}); applications.unshift(response.data); render(); saToast("Application submitted."); } catch (error) { saError(error); } }<br>api.get("/placements/open"), api.get("/me/applications"), api.get("/students?per_page=1")]); drives = result[0].data \|\| []; applications = result[1].data \|\| []; const id = result[2].data[0]?.id; if (id) attendance = Number((await api.get(`/students/${id}/attendance`)).data.percentage \|\| 0); render(); } catch (error) { saError(error); saEmpty("drives", "Unable to load placements."); saEmpty("apps", "Unable to load applications."); } } |
| assets/js/student/profile.js | api.get("/me/profile")).data \|\| {}); } catch (error) { saError(error); } }<br>api.upload("/me/profile/photo", formData); toast("Photo updated."); } catch (error) { saError(error); } }<br>api.patch("/me/profile", {phone: $("phone").value.trim(), email: $("email").value.trim(), guardian_phone: $("parent").value.trim(), address: $("addr").value.trim()}); toast("Profile saved."); } catch (error) { saFormErrors(form, error.errors); toast(error.message \|\| "Unable to save profile.", false); } })<br>api.post("/auth/change-password", {current_password: $("p0").value, new_password: $("p1").value}); form.reset(); toast("Password updated."); } catch (error) { saFormErrors(form, error.errors); toast(error.message \|\| "Unable to update password.", false); } }) |
| assets/js/student/readiness.js | api.post("/me/mock-interviews", {}); saToast("Mock interview request sent."); } catch (error) { saError(error); } }<br>api.get("/me/readiness").then(response => render(response.data \|\| {})).catch(error => { saError(error); saEmpty("factors", "Unable to load readiness."); saEmpty("tips", "Unable to load readiness."); }) |
| assets/js/student/timetable.js | api.get("/me/timetable").then(response => render(response.data \|\| {})).catch(error => { saError(error); saEmpty("body", "Unable to load timetable."); }) |
| assets/js/superadmin/attendance.js | api.get(`/batches/${$("batch").value}/students?per_page=100`), api.get(`/attendance?batch_id=${$("batch").value}&date=${$("date").value}`)]); students = result[0].data; records = result[1].data; marks = Object.fromEntries(records.map(item => [item.student_id, item.status])); render(); } catch (error) { saError(error); saEmpty("rows", "Unable to load attendance."); } }<br>api.post("/attendance/bulk", {batch_id:Number($("batch").value), date:$("date").value, records:Object.entries(marks).map(([student_id,status]) => ({student_id:Number(student_id), status}))}); saToast("Attendance saved."); } catch (error) { saError(error); } }<br>api.get("/batches?per_page=100").then(response => { $("batch").innerHTML = response.data.map(item => `<option value="${saEscape(item.id)}">${saEscape(item.code)}</option>`).join(""); load(); }).catch(error => { saError(error); saEmpty("rows", "Unable to load batches."); }) |
| assets/js/superadmin/courses.js | api.get("/courses?per_page=100"), api.get("/batches?per_page=100"), api.get("/staff?per_page=100")])<br>api.post("/courses", {name:$("cName").value.trim(), code:$("cName").value.trim().toUpperCase().replace(/\s+/g, "-"), total_fee:Number($("cFee").value), duration_months:Number($("cDur").value), description:$("cTools").value.trim()}); bootstrap.Modal.getInstance($("courseModal")).hide(); form.reset(); await load(); saToast("Course saved."); }<br>api.post("/batches", {code:$("bName").value.trim(), course_id:Number($("bCourse").value), trainer_id:Number($("bTrainer").value), time:$("bTime").value, start_date:$("bStart").value, seats:Number($("bSeats").value)}); bootstrap.Modal.getInstance($("batchModal")).hide(); form.reset(); await load(); saToast("Batch created."); } |
| assets/js/superadmin/dashboard.js | api.get("/dashboard/superadmin").then(response => render(response.data \|\| {})).catch(error => { saError(error); ["stats","admissions","drives","dues"].forEach(id => saEmpty(id, "Unable to load dashboard data.")); }) |
| assets/js/superadmin/fees.js | api.get("/fees/dues"), api.get("/payments"), api.get("/expenses"), api.get("/students?per_page=100")]); dues = result[0].data; payments = result[1].data; expenses = result[2].data; students = result[3].data; render(); } catch (error) { saError(error); saEmpty("stats", "Unable to load fee data."); ["payRows","dueRows","expRows"].forEach(id => saEmpty(id, "Unable to load fee data.")); } }<br>api.post("/payments", {student_id:Number($("pStu").value), installment_id:Number($("pStu").dataset.installmentId \|\| 0) \|\| undefined, amount:Number($("pAmt").value), mode:$("pMode").value}); bootstrap.Modal.getInstance($("payModal")).hide(); form.reset(); await load(); saToast("Payment saved."); } catch (error) { saFormErrors(form, error.errors); saError(error); } })<br>api.post("/expenses", {category:$("eCat").value, amount:Number($("eAmt").value), note:$("eNote").value.trim(), date:new Date().toISOString().slice(0, 10)}); bootstrap.Modal.getInstance($("expModal")).hide(); form.reset(); await load(); saToast("Expense saved."); } catch (error) { saFormErrors(form, error.errors); saError(error); } }) |
| assets/js/superadmin/forecast.js | api.get("/reports/course-demand")).data \|\| {}; render(); } catch (error) { saError(error); saEmpty("cards", "Unable to load forecast."); saEmpty("frows", "Unable to load forecast."); } } |
| assets/js/superadmin/leads.js | api.get("/leads?per_page=100"), api.get("/courses?per_page=100"), api.get("/staff?per_page=100")]); leads = result[0].data; courses = result[1].data; staff = result[2].data; const sources = [...new Set(leads.map(item => item.source).filter(Boolean))]; $("fSource").innerHTML = `<option value="">All sources</option>` + sources.map(value => `<option value="${saEscape(value)}">${saEscape(value)}</option>`).join(""); $("lCourse").innerHTML = courses.map(item => `<option value="${item.id}">${saEscape(item.name)}</option>`).join(""); $("lSource").innerHTML = sources.map(value => `<option>${saEscape(value)}</option>`).join(""); $("lCoun").innerHTML = staff.filter(item => item.designation === "counselor").map(item => `<option value="${item.id}">${saEscape(item.name)}</option>`).join(""); render(); } catch (error) { saError(error); saEmpty("rows", "Unable to load leads."); } }<br>api.patch(`/leads/${id}/status`, {status}); await load(); saToast("Lead status updated."); } catch (error) { saError(error); } }<br>api.post(`/leads/${id}/convert`, {student_code:studentCode, batch_id:lead?.batch_id \|\| undefined}); await load(); saToast(response.message \|\| "Lead converted."); } catch (error) { saError(error); } }<br>api.post("/leads", {name:$("lName").value.trim(), phone:$("lPhone").value.trim(), course_id:Number($("lCourse").value), source:$("lSource").value, counselor_id:Number($("lCoun").value), follow_up_on:$("lFollow").value, note:$("lNote").value.trim()}); bootstrap.Modal.getInstance($("leadModal")).hide(); form.reset(); await load(); saToast("Lead added."); } catch (error) { saFormErrors(form, error.errors); saError(error); } }) |
| assets/js/superadmin/performance.js | api.get("/reports/staff-performance")).data; const roles = [...new Set(records.map(item => item.designation).filter(Boolean))]; $("fRole").innerHTML = `<option value="">All roles</option>` + roles.map(item => `<option value="${saEscape(item)}">${saEscape(item)}</option>`).join(""); $("bands").textContent = "Performance scoring fields are not provided by the backend."; $("weights").textContent = "Performance weighting is unavailable until scoring fields are added."; render(); } catch (error) { saError(error); saEmpty("rows", "Unable to load performance data."); } } |
| assets/js/superadmin/placements.js | api.get("/drives?per_page=100"), api.get("/companies?per_page=100"), api.get("/applications?per_page=100"), api.get("/students?per_page=100"), api.get("/courses?per_page=100")]); drives = result[0].data; companies = result[1].data; applications = result[2].data; students = result[3].data; courses = result[4].data; render(); } catch (error) { saError(error); saEmpty("stats", "Unable to load placement data."); ["driveRows","placedRows","coRows"].forEach(id => saEmpty(id, "Unable to load placement data.")); } }<br>api.post("/companies", {name:$("dCo").value.trim(), contact:""})).data; await api.post("/drives", {company_id:company.id, title:$("dRole").value.trim(), role:$("dRole").value.trim(), drive_date:$("dDate").value, package:Number($("dPkg").value), course_id:Number($("dCourse").value) \|\| null, attendance_threshold:Number($("dAtt").value)}); bootstrap.Modal.getInstance($("driveModal")).hide(); form.reset(); await load(); saToast("Drive scheduled."); } catch (error) { saFormErrors(form, error.errors); saError(error); } }) |
| assets/js/superadmin/reports.js | api.get(`/reports/admissions?${params}`), api.get(`/reports/fees?${params}`), api.get(`/reports/attendance?${params}`)]) |
| assets/js/superadmin/settings.js | api.patch("/settings", payload()); form.classList.remove("was-validated"); saToast(message); } catch (error) { saFormErrors(form, error.errors); saError(error); }<br>api.get("/settings")).data \|\| {}; const fields = {academy_name:"aName", phone:"aPhone", email:"aEmail", gst_number:"aGst", address:"aAddr", receipt_prefix:"rPre", grace_period:"rGrace", minimum_attendance:"rMin", fee_due_reminders:"n1", absence_alerts:"n2", placement_announcements:"n3", weekly_summary:"n4"}; Object.entries(fields).forEach(([key, id]) => { if (values[key] == null \|\| !$(id)) return; if ($(id).type === "checkbox") $(id).checked = values[key] === true \|\| values[key] === "true"; else $(id).value = values[key]; }); } catch (error) { saError(error); ["aName","aPhone","aEmail","aGst","aAddr","rPre","rGrace","rMin"].forEach(id => { if ($(id)) $(id).setCustomValidity("Unable to load settings."); }); } }<br>api.patch("/settings", {fee_due_reminders:$("n1").checked, absence_alerts:$("n2").checked, placement_announcements:$("n3").checked, weekly_summary:$("n4").checked}); saToast("Notification settings saved."); } catch (error) { saError(error); } }<br>api.post("/auth/change-password", {current_password:$("p0").value, new_password:$("p1").value}); form.reset(); form.classList.remove("was-validated"); saToast("Password updated."); } catch (error) { saFormErrors(form, error.errors); saError(error); } })<br>api.get("/settings/backup?format=json"); const link = document.createElement("a"); link.href = URL.createObjectURL(new Blob([JSON.stringify(response.data, null, 2)], {type:"application/json"})); link.download = "academy-backup.json"; link.click(); } catch (error) { saError(error); } } |
| assets/js/superadmin/staff.js | api.get("/staff?per_page=100"), api.get("/staff/workload")]); staff = result[0].data; workloads = result[1].data; const roles = [...new Set(staff.map(item => item.designation).filter(Boolean))]; $("fRole").innerHTML = `<option value="">All roles</option>` + roles.map(item => `<option value="${saEscape(item)}">${saEscape(item)}</option>`).join(""); $("sRole").innerHTML = roles.map(item => `<option value="${saEscape(item)}">${saEscape(item)}</option>`).join(""); render(); }<br>api.post("/users", {name:$("sName").value.trim(), email, role:"staff", password}); await api.post("/staff", {user_id:user.data.id, name:$("sName").value.trim(), phone:$("sPhone").value.trim(), designation:$("sRole").value, staff_code:`STF-${Date.now().toString().slice(-6)}`, joined_on:$("sJoin").value, qualification:$("sSkill").value.trim()}); bootstrap.Modal.getInstance($("staffModal")).hide(); form.reset(); await load(); saToast("Staff added."); } |
| assets/js/superadmin/students.js | api.get("/students?per_page=100"), api.get("/courses?per_page=100"), api.get("/batches?per_page=100")]); students = result[0].data; courses = result[1].data; batches = result[2].data; $("fCourse").innerHTML = `<option value="">All courses</option>` + courses.map(item => `<option value="${saEscape(item.id)}">${saEscape(item.name)}</option>`).join(""); $("fCourseAdd").innerHTML = courses.map(item => `<option value="${saEscape(item.id)}">${saEscape(item.name)}</option>`).join(""); $("fCourseAdd").dispatchEvent(new Event("change")); render(); }<br>api.get(`/students/${id}/summary`); $("pName").textContent = student?.name \|\| "Student"; $("pBody").innerHTML = `<div class="mb-3"><b>${saEscape(student?.student_code)}</b><div class="text-secondary">${saEscape(student?.email \|\| "")}</div></div><div>Attendance: ${saEscape(summary.data.attendance_percentage ?? summary.data.percentage ?? "-")}%</div>`; bootstrap.Offcanvas.getOrCreateInstance($("profile")).show(); } catch (error) { saError(error); } }<br>api.post("/users", {name:$("fName").value.trim(), email, role:"student", password}); const year = new Date().getFullYear(); await api.post("/students", {user_id:user.data.id, student_code:`STU-${year}-${String(Date.now()).slice(-6)}`, name:$("fName").value.trim(), email, phone:$("fPhone").value.trim(), course_id:Number($("fCourseAdd").value), batch_id:Number($("fBatch").value), admission_date:$("fDob").value, guardian_phone:$("fParent").value.trim(), address:$("fAddr").value.trim()}); bootstrap.Modal.getInstance($("addModal")).hide(); form.reset(); await load(); saToast("Student added."); }<br>api.get("/students/export?format=csv"); const link = document.createElement("a"); link.href = URL.createObjectURL(new Blob([response.data], {type:"text/csv"})); link.download = "students.csv"; link.click(); } catch (error) { saError(error); } } |
| assets/js/superadmin/users.js | api.get("/users?per_page=100")).data; const roles = [...new Set(users.map(user => user.role).filter(Boolean))]; $("fRole").innerHTML = `<option value="">All roles</option>` + roles.map(role => `<option value="${saEscape(role)}">${saEscape(role)}</option>`).join(""); $("uRole").innerHTML = roles.map(role => `<option value="${saEscape(role)}">${saEscape(role)}</option>`).join(""); $("permHead").innerHTML = `<tr><th>Permissions</th><th>Status</th></tr>`; $("permRows").innerHTML = `<tr><td colspan="2" class="text-secondary">Role permissions are governed by the backend role policy.</td></tr>`; render(); } catch (error) { saError(error); saEmpty("rows", "Unable to load users."); } }<br>api.patch(`/users/${id}`, {is_active: active}); await load(); saToast("User status updated."); } catch (error) { saError(error); } }<br>api.post(`/users/${id}/reset-password`, {}); saToast(`Password reset. Temporary password: ${response.data.temporary_password}`); } catch (error) { saError(error); } }<br>api.post("/users", {name:$("uName").value.trim(), email:$("uEmail").value.trim(), role:$("uRole").value, password:$("uPwd").value}); bootstrap.Modal.getInstance($("userModal")).hide(); form.reset(); await load(); saToast("User created."); } catch (error) { saFormErrors(form, error.errors); saError(error); } }) |

## Remaining hardcoded arrays/sample markers

| JavaScript file | Evidence |
| --- | --- |
| assets/js/applications.js | 6: const stages = ["applied", "shortlisted", "interview", "selected", "rejected"]; |
| assets/js/face.js | 5: // Sample data: replace with API data later |
| assets/js/readiness.js | 6: // Sample data: replace with API data (and the ML model's score) later<br>39: const rows = [["Student","Batch","Score","Status","Weakest area"], ...students.map(s => [s.name, s.batch, score(s), cat(score(s))[0], LABEL[weakest(s)]])]; |
| assets/js/staff/dashboard.js | 6: const cards = [ |
| assets/js/student/assistant.js | 3: const chips = ["What is my attendance?", "How much fee do I have to pay?", "When is my next class?", "What deadlines do I have?", "Which drives can I apply to?"]; |
| assets/js/student/dashboard.js | 8: const stats = [["bi-calendar-check-fill", "Attendance", `${data.attendance_percentage ?? "-"}%`, "#dff3e8", "#177a4b"], ["bi-cash-coin", "Fee balance", `₹${Number(data.outstanding_dues \|\| 0).toLocaleString("en-IN")}`, "#dcebf7", "#1c5a8c"], ["bi-clipboard-data-fill", "Average marks", `${data.average_marks ?? "-"}%`, "#e3dcf5", "#4c3a96"], ["bi-briefcase-fill", "Open drives", data.open_drives ?? 0, "#fbeccd", "#8a5a06"]]; |
| assets/js/student/placements.js | 4: const steps = ["Applied", "Shortlisted", "Interview", "Selected"]; |
| assets/js/superadmin/dashboard.js | 5: const cards = [["bi-people-fill","Active students",data.students],["bi-journal-bookmark-fill","Running batches",data.active_batches],["bi-collection","Courses",data.courses],["bi-person-lines-fill","Open leads",data.leads]]; |
| assets/js/superadmin/leads.js | 4: const statuses = ["new", "contacted", "follow_up", "interested", "enrolled", "lost"];<br>13: const load = async () => { saLoading("rows"); try { const result = await Promise.all([api.get("/leads?per_page=100"), api.get("/courses?per_page=100"), api.get("/staff?per_page=100")]); leads = result[0].data; courses = result[1].data; staff = result[2].data; const sources = [...new Set(leads.map(item => item.source).filter(Boolean))]; $("fSource").innerHTML = `<option value="">All sources</option>` + sources.map(value => `<option value="${saEscape(value)}">${saEscape(value)}</option>`).join(""); $("lCourse").innerHTML = courses.map(item => `<option value="${item.id}">${saEscape(item.name)}</option>`).join(""); $("lSource").innerHTML = sources.map(value => `<option>${saEscape(value)}</option>`).join(""); $("lCoun").innerHTML = staff.filter(item => item.designation === "counselor").map(item => `<option value="${item.id}">${saEscape(item.name)}</option>`).join(""); render(); } catch (error) { saError(error); saEmpty("rows", "Unable to load leads."); } }; |
| assets/js/superadmin/performance.js | 8: const load = async () => { saLoading("rows"); try { records = (await api.get("/reports/staff-performance")).data; const roles = [...new Set(records.map(item => item.designation).filter(Boolean))]; $("fRole").innerHTML = `<option value="">All roles</option>` + roles.map(item => `<option value="${saEscape(item)}">${saEscape(item)}</option>`).join(""); $("bands").textContent = "Performance scoring fields are not provided by the backend."; $("weights").textContent = "Performance weighting is unavailable until scoring fields are added."; render(); } catch (error) { saError(error); saEmpty("rows", "Unable to load performance data."); } }; |
| assets/js/superadmin/staff.js | 13: try { const result = await Promise.all([api.get("/staff?per_page=100"), api.get("/staff/workload")]); staff = result[0].data; workloads = result[1].data; const roles = [...new Set(staff.map(item => item.designation).filter(Boolean))]; $("fRole").innerHTML = `<option value="">All roles</option>` + roles.map(item => `<option value="${saEscape(item)}">${saEscape(item)}</option>`).join(""); $("sRole").innerHTML = roles.map(item => `<option value="${saEscape(item)}">${saEscape(item)}</option>`).join(""); render(); } |
| assets/js/superadmin/users.js | 8: const load = async () => { saLoading("rows"); try { users = (await api.get("/users?per_page=100")).data; const roles = [...new Set(users.map(user => user.role).filter(Boolean))]; $("fRole").innerHTML = `<option value="">All roles</option>` + roles.map(role => `<option value="${saEscape(role)}">${saEscape(role)}</option>`).join(""); $("uRole").innerHTML = roles.map(role => `<option value="${saEscape(role)}">${saEscape(role)}</option>`).join(""); $("permHead").innerHTML = `<tr><th>Permissions</th><th>Status</th></tr>`; $("permRows").innerHTML = `<tr><td colspan="2" class="text-secondary">Role permissions are governed by the backend role policy.</td></tr>`; render(); } catch (error) { saError(error); saEmpty("rows", "Unable to load users."); } }; |

## Coverage gap table

This is a route-to-test text inventory; a role matrix is not currently generated by the suite.

| Route | Existing test evidence | Role-matrix tested |
| --- | --- | --- |
| / | no | no |
| /<path:filename> | yes | no |
| /api/v1/applications | yes | no |
| /api/v1/applications/<int:application_id> | yes | no |
| /api/v1/assessments | yes | no |
| /api/v1/attendance | yes | no |
| /api/v1/attendance/bulk | yes | no |
| /api/v1/attendance/monthly-summary | yes | no |
| /api/v1/auth/change-password | yes | no |
| /api/v1/auth/forgot-password | yes | no |
| /api/v1/auth/login | yes | no |
| /api/v1/auth/logout | yes | no |
| /api/v1/auth/me | yes | no |
| /api/v1/auth/refresh | yes | no |
| /api/v1/auth/reset-password | yes | no |
| /api/v1/batches | no | no |
| /api/v1/batches | no | no |
| /api/v1/batches/<int:batch_id> | yes | no |
| /api/v1/batches/<int:batch_id> | yes | no |
| /api/v1/certificates | no | no |
| /api/v1/certificates/<int:certificate_id>/download | yes | no |
| /api/v1/certificates/eligibility | yes | no |
| /api/v1/companies | yes | no |
| /api/v1/companies/<int:company_id> | yes | no |
| /api/v1/courses | yes | no |
| /api/v1/courses | yes | no |
| /api/v1/courses/<int:course_id> | yes | no |
| /api/v1/courses/<int:course_id> | yes | no |
| /api/v1/dashboard | no | no |
| /api/v1/dashboard/<role> | yes | no |
| /api/v1/dashboard/superadmin | yes | no |
| /api/v1/drives | yes | no |
| /api/v1/drives/<int:drive_id> | yes | no |
| /api/v1/fees/dues | yes | no |
| /api/v1/fees/expenses | yes | no |
| /api/v1/fees/expenses/<int:expense_id> | yes | no |
| /api/v1/fees/me | yes | no |
| /api/v1/fees/payments | yes | no |
| /api/v1/fees/payments | yes | no |
| /api/v1/fees/payments/<int:payment_id>/receipt | yes | no |
| /api/v1/fees/payments/<int:payment_id>/void | yes | no |
| /api/v1/fees/plans | yes | no |
| /api/v1/fees/plans | yes | no |
| /api/v1/health | yes | no |
| /api/v1/leads | yes | no |
| /api/v1/leads | yes | no |
| /api/v1/leads/<int:lead_id> | yes | no |
| /api/v1/leads/<int:lead_id> | yes | no |
| /api/v1/leads/<int:lead_id>/convert | yes | no |
| /api/v1/leads/<int:lead_id>/follow-ups | yes | no |
| /api/v1/leads/<int:lead_id>/status | yes | no |
| /api/v1/marks | yes | no |
| /api/v1/marks/bulk | yes | no |
| /api/v1/materials | yes | no |
| /api/v1/materials | yes | no |
| /api/v1/materials/<int:material_id> | yes | no |
| /api/v1/materials/<int:material_id>/download | yes | no |
| /api/v1/materials/upload | yes | no |
| /api/v1/me/applications | yes | no |
| /api/v1/me/assessments | yes | no |
| /api/v1/me/certificates | no | no |
| /api/v1/me/marks | yes | no |
| /api/v1/notifications | yes | no |
| /api/v1/notifications | yes | no |
| /api/v1/notifications/<int:notification_id>/read | yes | no |
| /api/v1/notifications/mine | yes | no |
| /api/v1/notifications/read-all | yes | no |
| /api/v1/notifications/unread | yes | no |
| /api/v1/placements/open | no | no |
| /api/v1/protected/staff-check | yes | no |
| /api/v1/protected/superadmin-check | yes | no |
| /api/v1/reports/admissions | no | no |
| /api/v1/reports/attendance | yes | no |
| /api/v1/reports/fees | yes | no |
| /api/v1/settings | yes | no |
| /api/v1/settings | yes | no |
| /api/v1/settings | yes | no |
| /api/v1/settings/backup | yes | no |
| /api/v1/settings/public | yes | no |
| /api/v1/staff | yes | no |
| /api/v1/staff | yes | no |
| /api/v1/staff/<int:staff_id> | yes | no |
| /api/v1/staff/<int:staff_id> | yes | no |
| /api/v1/staff/workload | yes | no |
| /api/v1/students | yes | no |
| /api/v1/students | yes | no |
| /api/v1/students/<int:student_id> | yes | no |
| /api/v1/students/<int:student_id> | yes | no |
| /api/v1/students/<int:student_id>/attendance | yes | no |
| /api/v1/students/export | yes | no |
| /api/v1/users | no | no |
| /api/v1/users | no | no |
| /api/v1/users/<int:user_id> | yes | no |
| /api/v1/users/<int:user_id> | yes | no |
| /api/v1/users/<int:user_id>/activate | yes | no |
| /api/v1/users/<int:user_id>/deactivate | yes | no |
| /api/v1/users/<int:user_id>/reset-password | yes | no |
| /static/<path:filename> | yes | no |

## Migration drift

Checked in an isolated copied backend and SQLite database:

- `flask db upgrade`: exit 0; all four revisions applied successfully.
- `flask db migrate -m "stage0 drift check"`: exit 0; Alembic reported `No changes in schema detected.`
- No new migration was generated beyond the copied baseline revisions.
