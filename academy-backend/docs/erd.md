# Academy Management System ERD

```mermaid
erDiagram
  USERS ||--o| STAFF : has
  USERS ||--o| STUDENTS : has
  USERS ||--o{ PASSWORD_RESET_TOKENS : requests
  COURSES ||--o{ BATCHES : contains
  STAFF ||--o{ BATCHES : trains
  COURSES ||--o{ STUDENTS : enrolls
  BATCHES ||--o{ STUDENTS : assigns
  STAFF ||--o{ LEADS : counsels
  LEADS ||--o| STUDENTS : converts
  STUDENTS ||--o{ ATTENDANCE : records
  STUDENTS ||--o{ FEE_PLANS : owns
  FEE_PLANS ||--o{ INSTALLMENTS : contains
  INSTALLMENTS ||--o{ PAYMENTS : receives
  STUDENTS ||--o{ PAYMENTS : makes
  BATCHES ||--o{ ASSESSMENTS : has
  ASSESSMENTS ||--o{ MARKS : records
  STUDENTS ||--o{ MARKS : earns
  BATCHES ||--o{ MATERIALS : contains
  COMPANIES ||--o{ PLACEMENT_DRIVES : hosts
  PLACEMENT_DRIVES ||--o{ APPLICATIONS : receives
  STUDENTS ||--o{ APPLICATIONS : submits
  STUDENTS ||--o{ CERTIFICATES : receives
  USERS ||--o{ NOTIFICATIONS : creates
  NOTIFICATIONS ||--o{ NOTIFICATION_READS : tracks
  USERS ||--o{ NOTIFICATION_READS : reads
  USERS ||--o{ AUDIT_LOGS : causes
  STUDENTS ||--o| FACE_ENROLLMENTS : enrolls
```

`expenses` and `settings` are standalone operational tables. Foreign keys are
indexed where they are used for ownership, filtering, or joins. Student,
staff, lead, and course records use soft deletion; financial and attendance
history is retained.
