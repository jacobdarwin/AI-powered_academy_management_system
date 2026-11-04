# QA Defects

## Open defects

### DEF-001: Deactivated users retain access through existing role-protected tokens
- Severity: Critical
- Type: Security
- Area / module: Authentication > Token lifecycle / RBAC
- Role(s) affected: Any deactivated user with an existing JWT; reproduced with superadmin
- Environment: Python 3.14.5, Flask test client, in-memory SQLite
- Steps to reproduce:
  1. Log in as `admin@example.com` and retain the access token.
  2. Set that user's `is_active` field to `False`.
  3. Call `GET /api/v1/protected/superadmin-check` with the retained token.
- Expected: The existing token is rejected with HTTP 401 after deactivation.
- Actual: The endpoint returns HTTP 200.
- Evidence: `tests/test_stage2_auth_rbac.py::test_deactivated_user_token_is_rejected_by_role_guard`; assertion expected 401, received 200.
- Suggested cause: `app/auth.py` `roles_required()` verifies the JWT and role claim but does not check the current user's active state.
- Suggested fix: Check the token subject's current `User.is_active` state in the shared authorization guard and return 401 when inactive.

No other Stage 2 defects found.

## Resolved test-infrastructure issue

The first infrastructure run returned `1 failed, 2 passed` because the fixture returned expired SQLAlchemy ORM instances. The fixture now returns scalar IDs for batches and students; the corrected run passes. This was a test-fixture defect and is not an application defect.

## Counts

| Severity | Open |
|---|---:|
| Blocker | 0 |
| Critical | 1 |
| Major | 0 |
| Minor | 0 |
| Cosmetic | 0 |
