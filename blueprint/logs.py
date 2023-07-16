from flask import Blueprint, jsonify, request

from models.logsModel import db, Logs
from schema.modelSchema import logs_schema
from auth.identityAuth import role_auth_require

from utils.tool import operation_res_build
from sqlalchemy import func

import logger

logs_bp = Blueprint("logs", __name__, url_prefix="/api/logs")


@logs_bp.route("/", methods=["GET"])
@role_auth_require(auth_roles=["system", "unit_manager"])
def logs_request(role, identity):
    """
    日志信息获取
    """
    try:
        if role == "system":
            logs = Logs.query.offset(request.args.get("offset")).limit(request.args.get("limit")).all()
            total = db.session.query(func.count(Logs.log_id)).scalar()
        else:
            logs = Logs.query.filter(Logs.unit_id_copy == identity["unit_id"])\
                .offset(request.args.get("offset")).limit(request.args.get("limit")).all()

            total = db.session.query(func.count(Logs.log_id)).filter(Logs.unit_id_copy == identity["unit_id"]).scalar()
    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "load logs failed")
        logger.exception(e)
        return jsonify(operation_res_build("load logs failed", False))

    return jsonify(operation_res_build("load logs ok", True, data={"logs": logs_schema.dump(logs), "total": total}))

