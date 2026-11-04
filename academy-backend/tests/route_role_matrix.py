"""Reviewable route/role expectations consumed by later RBAC stages."""

ROLES = ("superadmin", "staff", "student")


def expected_roles(rule, endpoint, method=None):
    if not rule.startswith("/api/v1/"):
        return ()
    if rule in {"/api/v1/health", "/api/v1/auth/login", "/api/v1/auth/refresh",
                "/api/v1/auth/forgot-password", "/api/v1/auth/reset-password",
                "/api/v1/settings/public"}:
        return ()
    if endpoint == "api.placements.applications" and method == "POST":
        return ("student",)
    if endpoint.endswith("superadmin_check"):
        return ("superadmin",)
    if endpoint.endswith("staff_check"):
        return ("staff", "superadmin")
    if endpoint.startswith("api.auth.") or endpoint.startswith("api.protected."):
        return ("superadmin", "staff", "student")
    if endpoint.startswith("api.academics."):
        if endpoint in {"api.academics.my_marks", "api.academics.my_assessments"}:
            return ("student",)
        if endpoint in {"api.academics.student_attendance", "api.academics.list_marks"}:
            return ("superadmin", "staff", "student")
        return ("superadmin", "staff")
    if endpoint.startswith("api.fees."):
        if endpoint == "api.fees.my_fees":
            return ("student",)
        if endpoint == "api.fees.payment_receipt":
            return ("superadmin", "staff", "student")
        return ("superadmin", "staff")
    if endpoint.startswith("api.placements."):
        if endpoint in {"api.placements.open_drives", "api.placements.applications",
                        "api.placements.my_applications", "api.placements.certificate_eligibility",
                        "api.placements.my_certificates", "api.placements.download_certificate"}:
            return ("superadmin", "staff", "student")
        return ("superadmin", "staff")
    if endpoint.startswith("api.resources."):
        if endpoint in {"api.resources.list_users", "api.resources.create_user",
                        "api.resources.get_user", "api.resources.update_user",
                        "api.resources.activate_user", "api.resources.deactivate_user",
                        "api.resources.reset_user_password", "api.resources.create_course",
                        "api.resources.update_course", "api.resources.delete_course",
                        "api.resources.list_staff", "api.resources.staff_workload",
                        "api.resources.create_staff", "api.resources.update_staff",
                        "api.resources.delete_staff", "api.resources.create_batch",
                        "api.resources.update_batch", "api.resources.delete_batch"}:
            return ("superadmin",)
        if endpoint == "api.resources.export_students":
            return ("superadmin", "staff")
        return ("superadmin", "staff", "student")
    if endpoint.startswith("api.leads."):
        return ("superadmin", "staff")
    if endpoint.startswith("api.phase8."):
        if endpoint in {"api.phase8.dashboard", "api.phase8.role_dashboard"}:
            return ("superadmin", "staff", "student")
        if endpoint == "api.phase8.superadmin_dashboard":
            return ("superadmin",)
        if endpoint == "api.phase8.public_settings":
            return ()
        if endpoint in {"api.phase8.list_materials", "api.phase8.download_material",
                        "api.phase8.list_notifications", "api.phase8.list_my_notifications",
                        "api.phase8.unread_notifications", "api.phase8.mark_notification_read",
                        "api.phase8.mark_all_notifications_read"}:
            return ("superadmin", "staff", "student")
        if endpoint in {"api.phase8.upload_material", "api.phase8.delete_material",
                        "api.phase8.create_notification"}:
            return ("superadmin", "staff")
        return ("superadmin", "staff")
    return ("superadmin", "staff", "student")


def build_matrix(app):
    matrix = []
    for rule in sorted(app.url_map.iter_rules(), key=lambda item: (item.rule, sorted(item.methods))):
        if not rule.rule.startswith("/api/v1/"):
            continue
        for method in sorted(rule.methods - {"HEAD", "OPTIONS"}):
            matrix.append({
                "method": method,
                "path": rule.rule,
                "endpoint": rule.endpoint,
                "allowed_roles": expected_roles(rule.rule, rule.endpoint, method),
            })
    return matrix
