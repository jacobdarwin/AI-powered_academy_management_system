# API contract

## Conventions

Base path: `/api/v1`. All responses are JSON using:

```json
{ "success": true, "data": {}, "message": "", "meta": {} }
```

Errors use:

```json
{ "success": false, "message": "Validation failed", "errors": { "field": ["reason"] } }
```

List endpoints accept `page`, `per_page` (maximum 100), `q`, `sort`, and
`order`, plus the resource-specific filters below. Authentication is
`Authorization: Bearer <access_token>`. `204` responses have no body.

## Authentication and public endpoints

| Method | Path | Request | Response / roles |
|---|---|---|---|
| GET | `/health` | — | Service status; public |
| GET | `/settings/public` | — | Academy name/logo/currency; public |
| POST | `/auth/login` | `{role,userId,password}` | `{access_token,refresh_token,user:{id,name,role,designation,login_id}}`; public |
| POST | `/auth/refresh` | refresh token | New access token; authenticated refresh token |
| POST | `/auth/logout` | — | Revoke token; authenticated |
| GET | `/auth/me` | — | Current user and staff/student profile; authenticated |
| POST | `/auth/change-password` | `{current_password,new_password}` | Updated status; authenticated |
| POST | `/auth/forgot-password` | `{identifier}` | Constant generic confirmation; public |
| POST | `/auth/reset-password` | `{token,password}` | Updated status; public with valid one-time token |

## Dashboard and identity

| Method | Path | Request/query | Allowed roles |
|---|---|---|---|
| GET | `/dashboard/superadmin` | optional date range | superadmin |
| GET | `/dashboard/staff` | — | staff |
| GET | `/dashboard/student` | — | student |
| GET | `/me/profile` | — | student |
| PATCH | `/me/profile` | `{phone,email,guardian_name,guardian_phone,address}` | student |
| POST | `/me/profile/photo` | multipart photo | student |
| GET | `/staff/me` | — | staff |
| PATCH | `/staff/me` | `{name,phone,email}` | staff |
| GET | `/staff/me/batches` | list parameters | staff |
| GET | `/me/timetable` | `from,to` | student; trainer |

Dashboard data includes KPI cards, chart series, recent admissions, drives,
dues, classes, deadlines, news, and the IDs needed by the existing renderers.

## Users, staff, courses, batches, and students

| Method | Path | Request/query | Allowed roles |
|---|---|---|---|
| GET/POST | `/users` | list filters / `{name,email,role,password}` | superadmin |
| GET/PATCH/DELETE | `/users/{id}` | user fields | superadmin |
| POST | `/users/{id}/activate` | — | superadmin |
| POST | `/users/{id}/deactivate` | — | superadmin |
| POST | `/users/{id}/reset-password` | optional password | superadmin |
| PATCH | `/users/{id}/role` | `{role,designation}` | superadmin |
| GET/POST | `/staff` | list filters / staff fields | superadmin |
| GET/PATCH/DELETE | `/staff/{id}` | staff fields | superadmin |
| GET | `/staff/workload` | filters | superadmin |
| GET/POST | `/courses` | list filters / `{name,code,total_fee,duration_months,description}` | superadmin; read for staff/student |
| GET/PATCH/DELETE | `/courses/{id}` | course fields | superadmin |
| GET/POST | `/batches` | filters / `{code,course_id,trainer_id,time,start_date,seats}` | superadmin |
| GET/PATCH/DELETE | `/batches/{id}` | batch fields | superadmin; permitted staff |
| GET | `/batches/{id}/students` | list parameters | superadmin; assigned staff |
| GET/POST | `/students` | filters / admission fields | superadmin; counselor for create/edit |
| GET/PATCH | `/students/{id}` | student fields | superadmin; permitted staff |
| GET | `/students/{id}/summary` | — | superadmin; permitted staff |
| POST | `/students/{id}/photo` | multipart photo | superadmin; permitted staff |
| GET | `/students/export` | filters and format=csv | superadmin; permitted staff |

Student IDs are generated as `STU-<year>-<sequence>` and staff IDs as
`STF-<sequence>`. Deletion is soft deletion where applicable.

## Leads and admissions

| Method | Path | Request/query | Allowed roles |
|---|---|---|---|
| GET/POST | `/leads` | `q,source,follow_up,status` / lead fields | superadmin; counselor |
| GET/PATCH | `/leads/{id}` | lead fields | superadmin; counselor |
| POST | `/leads/{id}/follow-ups` | `{date,note}` | superadmin; counselor |
| PATCH | `/leads/{id}/status` | `{status}` | superadmin; counselor |
| POST | `/leads/{id}/convert` | optional fee-plan/installments | superadmin; counselor |

Conversion atomically creates the student and user, links the lead, generates
a temporary password, and optionally creates a fee plan.

## Attendance, marks, and materials

| Method | Path | Request/query | Allowed roles |
|---|---|---|---|
| POST | `/attendance/bulk` | `{batch_id,date,records:[{student_id,status,note}]}` | superadmin; trainer for own batches |
| GET | `/attendance` | `batch_id,date,status` | superadmin; trainer own; student own only |
| GET | `/students/{id}/attendance` | `from,to,month` | superadmin; permitted staff; self only for student |
| GET | `/attendance/monthly-summary` | `batch_id,month` | superadmin; trainer own; student own |
| GET/POST | `/assessments` | filters / `{batch_id,title,type,max_marks,date}` | superadmin; trainer own |
| POST | `/marks/bulk` | `{assessment_id,records:[{student_id,marks,feedback}]}` | superadmin; trainer own |
| GET | `/marks` | `student_id,batch_id,assessment_id` | permitted staff; student self only |
| GET | `/me/marks` | — | student |
| GET | `/me/assessments` | — | student |
| POST | `/materials` | multipart `{title,type,batch_id,file}` | superadmin; trainer own |
| GET | `/materials` | `q,type,batch_id` | permitted roles |
| GET | `/materials/{id}/download` | — | authorized user |
| DELETE | `/materials/{id}` | — | superadmin; owner trainer |
| GET | `/me/materials` | `q,type` | student |

Attendance rejects future dates and enforces batch ownership. Marks reject
values above `max_marks`. The default attendance calculation is configurable.

## Fees, payments, and expenses

| Method | Path | Request/query | Allowed roles |
|---|---|---|---|
| GET/POST | `/fee-plans` | student/status filters / installments | superadmin; accounts |
| GET/PATCH | `/fee-plans/{id}` | plan/installment fields | superadmin; accounts |
| POST | `/payments` | `{student_id,installment_id?,amount,mode,reference}` | superadmin; accounts |
| GET | `/payments` | filters | superadmin; accounts |
| POST | `/payments/{id}/void` | `{reason}` | superadmin; accounts |
| GET | `/payments/{id}/receipt` | `format=json|pdf` | superadmin; accounts; owning student |
| GET | `/fees/dues` | filters | superadmin; accounts; counselor |
| GET | `/me/fees` | — | student |
| GET | `/me/payments` | — | student |
| GET/POST | `/expenses` | filters / `{category,amount,note,date}` | superadmin; accounts |
| PATCH | `/expenses/{id}` | expense fields | superadmin; accounts |

Money uses decimal values, payments cannot overpay, payments are never
deleted, and receipt numbers are generated transactionally as `RC-####`.

## Placements, applications, certificates, and notifications

| Method | Path | Request/query | Allowed roles |
|---|---|---|---|
| GET/POST | `/companies` | filters / `{name,website,contact}` | superadmin; placement officer |
| GET/PATCH | `/companies/{id}` | company fields | superadmin; placement officer |
| GET/POST | `/drives` | filters / drive fields | superadmin; placement officer |
| GET/PATCH | `/drives/{id}` | drive fields/status | superadmin; placement officer |
| GET | `/placements/open` | course/status/date filters | student |
| GET/POST | `/applications` | filters / `{drive_id}` | staff read; student creates own |
| GET/PATCH | `/applications/{id}` | `{status,offer_details}` | superadmin; placement officer |
| GET | `/me/applications` | — | student |
| GET | `/reports/placement-readiness` | `q,batch_id` | superadmin; staff |
| GET | `/me/readiness` | — | student |
| POST | `/me/mock-interviews` | booking fields | student |
| GET | `/me/certificates` | — | student |
| GET | `/certificates/eligibility` | `student_id?` | superadmin; student self |
| POST | `/certificates` | `{student_id}` | superadmin |
| GET | `/certificates/{id}/download` | PDF | authorized user |
| GET | `/notifications/mine` | `unread` | authenticated |
| GET | `/notifications/unread-count` | — | authenticated |
| POST | `/notifications` | `{title,message,audience,audience_ref_id}` | superadmin; permitted staff |
| POST | `/notifications/{id}/read` | — | recipient |
| POST | `/notifications/read-all` | — | authenticated |

Applications enforce open-drive, course, attendance, marks, and duplicate
checks. A selected application stores offer data and updates placement status.

## Reports, settings, assistant, and exports

| Method | Path | Request/query | Allowed roles |
|---|---|---|---|
| GET | `/reports/admissions` | `from,to,format` | superadmin |
| GET | `/reports/fees` | `from,to,format` | superadmin; accounts |
| GET | `/reports/outstanding-dues` | filters, format | superadmin; accounts |
| GET | `/reports/attendance` | `from,to,batch_id,format` | superadmin; trainer own |
| GET | `/reports/placements` | `from,to,format` | superadmin; placement officer |
| GET | `/reports/course-demand` | `course_id?` | superadmin |
| GET | `/reports/staff-performance` | `role?` | superadmin |
| PATCH | `/settings` | settings key/value fields | superadmin |
| GET | `/settings` | — | superadmin |
| GET | `/settings/backup` | `format=json` | superadmin |
| POST | `/assistant/messages` | `{message,conversation_id?}` | student |

Report endpoints return the common envelope with chart series and tabular
rows; `format=csv` returns a downloadable CSV and `format=pdf` returns a
downloadable document where supported. The assistant contract is provisional
until the product decision in the frontend audit is resolved.

## Authorization matrix

* `superadmin`: full access to all administrative resources.
* `trainer`: own batches for attendance, marks, materials, and student reads;
  own profile and assigned-batch timetable.
* `counselor`: leads and admissions; permitted student reads/edits.
* `placement_officer`: companies, drives, applications, and placement reports.
* `accounts`: fees, payments, expenses, and fee reports.
* `student`: own profile, timetable, attendance, fees, marks, materials,
  placements, certificates, notifications, and assistant only.

All object-level checks must derive ownership from the JWT and must not accept
an arbitrary student identity from a student request.

## Contract decisions still required

The following paths are placeholders until product decisions are made:
payment-gateway callbacks, face-recognition provider/storage, assistant
provider, mock-interview workflow, branch-manager role mapping, SMTP
configuration, and whether the backend serves `login-page/` in place or from a
new `frontend/` directory.
