# QA Traceability

Stage 1 establishes infrastructure. Unimplemented checks are explicitly marked for their planned stage.

## Section 6 business rules

| Rule | Test coverage |
|---|---|
| Sequential staff codes | NOT COVERED — Stage 4 |
| Sequential student codes | NOT COVERED — Stage 4 |
| Gap-free unique receipts and rollback behavior | Existing receipt tests; expanded business-rule coverage — Stage 4 |
| Fee-plan installment totals | Existing fee tests; full boundary coverage — Stage 4 |
| Partial/full/overdue fee status | Existing partial coverage; Stage 4 |
| Overpayment and money precision | Existing overpayment test; Stage 4 |
| Void reason, balance restoration, audit, no delete | Existing partial coverage; Stage 4 |
| Attendance uniqueness and updates | Existing partial coverage; Stage 4 |
| Future dates and wrong-batch rejection | Existing partial coverage; Stage 4 |
| Attendance percentage edge cases | NOT COVERED — Stage 4 |
| Atomic bulk attendance | NOT COVERED — Stage 4 |
| Marks bounds and uniqueness | Existing partial coverage; Stage 4 |
| Lead conversion transaction | NOT COVERED — Stage 4 |
| Batch capacity | NOT COVERED — Stage 4 |
| Placement eligibility and duplicate applications | Existing partial coverage; Stage 4 |
| Certificate eligibility and ownership | Existing partial coverage; Stage 4 |
| Lockout and inactive users | NOT COVERED — Stage 2 |
| Reset-token lifecycle | NOT COVERED — Stage 2 |
| Soft-delete behavior | NOT COVERED — Stage 4/5 |

## Section 8 security checks

| Security check | Test coverage |
|---|---|
| Object-level student isolation | Existing targeted tests; full matrix — Stage 3 |
| Trainer batch isolation | Existing targeted test; full checks — Stage 3 |
| Staff privilege escalation | NOT COVERED — Stage 3 |
| Deactivated-token behavior | NOT COVERED — Stage 2/3 |
| Password/token disclosure | NOT COVERED — Stage 2/3 |
| Brute-force/rate limiting | NOT COVERED — Stage 2 |
| User enumeration | NOT COVERED — Stage 2 |
| Injection and output handling | NOT COVERED — Stage 3/5 |
| Mass assignment | NOT COVERED — Stage 3/5 |
| Upload/path traversal security | NOT COVERED — Stage 6 |
| Configuration/dependency/security headers | NOT COVERED — Stage 6 |

## Stage 1 infrastructure

| Requirement | Evidence |
|---|---|
| Required actors | `tests/conftest.py::actors`, `test_infrastructure.py::test_actor_fixture_contains_required_roles` |
| Frozen time | `tests/conftest.py::frozen_time`, `test_infrastructure.py::test_frozen_time_fixture_is_deterministic` |
| Route x role matrix | `tests/route_role_matrix.py`, `test_infrastructure.py::test_route_role_matrix_covers_every_api_route` |

## Stage 2 authentication and RBAC

| Check | Evidence |
|---|---|
| Missing-token rejection for protected API routes | `tests/test_stage2_auth_rbac.py::test_protected_routes_reject_missing_tokens` |
| Route x role forbidden-role matrix | `tests/test_stage2_auth_rbac.py::test_route_role_matrix_enforces_forbidden_roles` |
| Expired, malformed, wrong-key, and tampered tokens | `tests/test_stage2_auth_rbac.py::test_expired_malformed_wrong_key_and_tampered_tokens_are_rejected` |
| Inactive and locked login rejection | `tests/test_stage2_auth_rbac.py::test_inactive_and_locked_users_cannot_login` |
| Generic forgot-password response and single-use reset token | `tests/test_stage2_auth_rbac.py::test_forgot_password_is_generic_and_reset_tokens_are_single_use` |
| Expired reset token rejection | `tests/test_stage2_auth_rbac.py::test_expired_reset_token_is_rejected` |
| Deactivated token rejected by `/auth/me` | `tests/test_stage2_auth_rbac.py::test_deactivated_user_token_is_rejected_by_me` |
| Deactivated token rejected by role guard | **FAIL — DEF-001** |
