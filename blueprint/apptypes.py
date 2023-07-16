from flask import Blueprint, jsonify, request

from models.apptypesModel import AppTypes, db
from schema.modelSchema import app_types_schema

from utils.tool import operation_res_build
from utils.log import log_info_record, LOG_ACTIONS

from auth.identityAuth import role_auth_require
import logger


app_types_bp = Blueprint("app_types", __name__, url_prefix="/api/app_types")


@app_types_bp.route("/", methods=["GET"])
@role_auth_require(grant_all=True)
def app_types_request(role, identity):
    try:
        app_types = AppTypes.query.all()
    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "load app_types failed")
        logger.exception(e)
        return jsonify(operation_res_build("load app_types failed", False))

    return jsonify(operation_res_build("load app_types ok", True, data=app_types_schema.dump(app_types)))


@app_types_bp.route("/<int:type_id>", methods=["GET"])
@role_auth_require(grant_all=True)
def app_types_by_id_request(role, identity, type_id):
    try:
        app_types = AppTypes.query.filter(AppTypes.type_id == type_id).first()

        if app_types is None:
            return jsonify(operation_res_build("the app_types is not exist", False))

    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "load app_types failed")
        logger.exception(e)
        return jsonify(operation_res_build("load app_types failed", False))

    return jsonify(operation_res_build("load app_types ok", True, data=app_types_schema.dump(app_types)))


@app_types_bp.route("/", methods=["POST"])
@role_auth_require(auth_roles=["system"])
@log_info_record(LOG_ACTIONS["ADD"])
def app_type_add(role, identity):
    data = request.get_json()

    type_name = data.get("type_name")
    type_memo = data.get("type_memo")

    try:
        if len(AppTypes.query.filter(AppTypes.type_name == type_name).all()):
            return jsonify(operation_res_build("the role exist", False)), False

        db.session.add(AppTypes(type_name, type_memo))
        db.session.commit()
    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "a error happened in addition")
        logger.exception(e)
        return jsonify(operation_res_build("a error happened in addition", False)), False

    return jsonify(operation_res_build("addition ok", True)), False


@app_types_bp.route("/<int:type_id>", methods=["DELETE"])
@role_auth_require(auth_roles=["system"])
@log_info_record(LOG_ACTIONS["DEL"])
def app_type_delete(role, identity, type_id):
    try:
        db.session.delete(AppTypes.query.filter(AppTypes.type_id == type_id).first())
        db.session.commit()
    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "a error happened in addition")
        logger.exception(e)
        return jsonify(operation_res_build("a error happened in deletion", False)), False

    return jsonify(operation_res_build("deletion ok", True)), True
