from typing import Any

from flask import jsonify


def success(data: Any = None, message: str = "", status: int = 200, meta: dict | None = None):
    return jsonify({"success": True, "data": data, "message": message, "meta": meta or {}}), status


def failure(message: str, status: int = 400, errors: dict | None = None):
    body = {"success": False, "message": message}
    if errors:
        body["errors"] = errors
    return jsonify(body), status
