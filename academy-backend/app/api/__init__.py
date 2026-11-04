from flask import Blueprint

from ..responses import success

api = Blueprint("api", __name__, url_prefix="/api/v1")


@api.get("/health")
def health():
    return success({"status": "ok"})


from .auth import auth_api
from .protected import protected_api
from .resources import resources_api
from .leads import leads_api
from .academics import academics_api
from .fees import fees_api
from .placements import placements_api
from .phase8 import phase8_api

api.register_blueprint(auth_api)
api.register_blueprint(protected_api)
api.register_blueprint(resources_api)
api.register_blueprint(leads_api)
api.register_blueprint(academics_api)
api.register_blueprint(fees_api)
api.register_blueprint(placements_api)
api.register_blueprint(phase8_api)
