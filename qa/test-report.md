# Stage 2 QA Test Report

## Scope

Stage 2 covered authentication, token lifecycle, lockout, password reset, deactivation behavior, and the route × role matrix.

## Stage 1 infrastructure retained

Added reusable Stage 1 test infrastructure only:

- Actor fixture for superadmin, two trainers, counselor, placement officer, accounts staff, two students in separate batches, inactive user, and locked user.
- `auth_headers` login helper.
- Frozen clock fixture using `freezegun`.
- Route x role matrix covering every registered `/api/v1` method/path pair.

No application behavior was changed.

## Stage 2 tests

- Added: 8 Stage 2 authentication/RBAC tests.
- Existing regression tests retained.

Focused passing command and raw output:

```text
py -m pytest -q tests/test_stage2_auth_rbac.py
.......                                                                  [100%]
7 passed in 6.06s
```

Focused defect reproduction:

```text
py -m pytest -q tests/test_stage2_auth_rbac.py::test_deactivated_user_token_is_rejected_by_role_guard
F                                                                        [100%]
1 failed in 0.74s
```

Full regression command and raw output:

```text
py -m pytest -q --disable-warnings
.....................................F                                   [100%]
1 failed, 37 passed, 5 warnings in 29.25s
```

Coverage command and raw summary:

```text
py -m pytest --cov=app --cov-report=term-missing -q --disable-warnings
TOTAL                     2126    456    79%
1 failed, 37 passed, 23 warnings in 29.82s
```

## Coverage

Current application coverage is **79%** overall. `app/services` does not exist, so service-package coverage is not applicable.

## Not tested

- Object-level isolation and security checks: Stage 3.
- Business rules: Stage 4.
- Validation and error sweep: Stage 5.
- Uploads, static analysis, and dependency audit: Stage 6.
- Browser/frontend flows: Stage 7.

## Result

Stage 2 tests exposed one open authentication defect. Do not proceed to release.
