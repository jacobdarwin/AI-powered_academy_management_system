from tests.route_role_matrix import ROLES, build_matrix


def test_actor_fixture_contains_required_roles(actors):
    assert {"STF-TRAINER-A", "STF-TRAINER-B", "STF-COUNSELOR",
            "STF-PLACEMENT", "STF-ACCOUNTS"} <= set(actors["users"])
    assert {"STU-TEST-A", "STU-TEST-B", "STU-INACTIVE", "STU-LOCKED"} <= set(actors["users"])
    assert actors["batches"]["a"] != actors["batches"]["b"]


def test_frozen_time_fixture_is_deterministic(frozen_time):
    from datetime import datetime, timezone

    assert datetime.now(timezone.utc).isoformat().startswith("2026-11-03T12:00:00")


def test_route_role_matrix_covers_every_api_route(app):
    matrix = build_matrix(app)
    covered = {(row["method"], row["path"]) for row in matrix}
    expected = {
        (method, rule.rule)
        for rule in app.url_map.iter_rules()
        if rule.rule.startswith("/api/v1/")
        for method in rule.methods - {"HEAD", "OPTIONS"}
    }
    assert covered == expected
    assert all(set(row["allowed_roles"]) <= set(ROLES) for row in matrix)
