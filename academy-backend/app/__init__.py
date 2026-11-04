from pathlib import Path

from flask import Flask, send_from_directory
from .config import get_config
from .errors import register_error_handlers
from .extensions import cors, db, jwt, limiter, migrate


def create_app(config_class=None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class or get_config())
    app.config.setdefault("JWT_ACCESS_TOKEN_EXPIRES", 1800)
    app.config.setdefault("JWT_REFRESH_TOKEN_EXPIRES", 604800)
    app.config["FRONTEND_DIR"] = Path(app.config["FRONTEND_DIR"]).resolve()

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    limiter.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

    from . import models  # noqa: F401
    from .api import api
    from .auth import jwt_is_revoked

    @jwt.token_in_blocklist_loader
    def token_in_blocklist(_jwt_header, jwt_payload):
        return jwt_is_revoked(jwt_payload)

    app.register_blueprint(api)
    register_error_handlers(app)

    @app.after_request
    def security_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        if not app.debug:
            response.headers.setdefault("Strict-Transport-Security", "max-age=31536000")
        return response

    @app.cli.command("seed")
    def seed_command():
        from .seed import seed_demo

        seed_demo()
        print("Demo seed complete.")
        print("Superadmin: admin@youracademy.com / Admin@12345")
        print("Staff: STF-0001..STF-0004 / Staff@12345")
        print("Students: STU-2026-0001..STU-2026-0040 / Student@12345")

    @app.get("/")
    def frontend_index():
        return send_from_directory(app.config["FRONTEND_DIR"], "index.html")

    @app.get("/<path:filename>")
    def frontend_file(filename: str):
        frontend = app.config["FRONTEND_DIR"]
        requested = (frontend / filename).resolve()
        if frontend not in requested.parents:
            return {"success": False, "message": "Not found"}, 404
        return send_from_directory(frontend, filename)

    return app
