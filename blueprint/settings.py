from flask import Blueprint, jsonify, request

from models.settingsModel import db, Settings
from schema.modelSchema import settings_schema_single

from utils.log import log_info_record, LOG_ACTIONS
from utils.tool import operation_res_build
from auth.identityAuth import role_auth_require

import logger
settings_bp = Blueprint("settings", __name__, url_prefix="/api/settings")


@settings_bp.route("/", methods=["GET"])
@role_auth_require(grant_all=True)
def settings_request(role, identity):
    try:
        setting = Settings.query.first()
        return jsonify(operation_res_build("load settings ok", True, settings=settings_schema_single.dump(setting)))
    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "load settings failed")
        logger.exception(e)
        return jsonify(operation_res_build("load settings failed", False))


@settings_bp.route("/", methods=["PUT"])
@role_auth_require(auth_roles=["system"])
@log_info_record(LOG_ACTIONS["MOD"])
def settings_update(role, identity):
    if role != "system":
        return jsonify(operation_res_build("only system manager can update this", False)), False

    data = request.get_json()

    app_refresh = data.get("app_refresh")
    app_version = data.get("app_version")
    try:
        Settings.query.update({
            "app_refresh": app_refresh,
            "app_version": app_version
        })
        db.session.commit()
    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "load settings failed")
        logger.exception(e)
        return jsonify(operation_res_build("load settings failed", False)), False

    return jsonify(operation_res_build("update settings ok", True)), True
