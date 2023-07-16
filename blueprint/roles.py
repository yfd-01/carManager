from flask import Blueprint, jsonify, request
from models.rolesModel import db, Roles
from schema.modelSchema import roles_schema

from auth.identityAuth import role_auth_require

from utils.tool import operation_res_build
from utils.log import LOG_ACTIONS, log_info_record
import logger

roles_bp = Blueprint("roles", __name__, url_prefix="/api/roles")


@roles_bp.route("/", methods=["GET"])
@role_auth_require(auth_roles=["system"])
def roles_request(role, identity):
    """
    role信息获取
    """
    try:
        roles = Roles.query.all()
    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "load roles failed")
        logger.exception(e)
        return jsonify(operation_res_build("load roles failed", False))

    return jsonify(operation_res_build("load roles ok", True, data=roles_schema.dump(roles)))


@roles_bp.route("/", methods=["POST"])
@role_auth_require(auth_roles=["system"])
@log_info_record(LOG_ACTIONS["ADD"])
def role_add(role, identity):
    """
    role添加
    """
    data = request.get_json()

    role_name = data.get("role_name")
    role_memo = data.get("role_memo")

    try:
        if len(Roles.query.filter(Roles.role_name == role_name).all()):
            return jsonify(operation_res_build("the role exist", False)), False

        db.session.add(Roles(role_name, role_memo))
        db.session.commit()
    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "a error happened in addition")
        logger.exception(e)
        return jsonify(operation_res_build("a error happened in addition", False)),False

    return jsonify(operation_res_build("addition ok", True)),True


@roles_bp.route("/<int:role_id>", methods=["PUT"])
@role_auth_require(auth_roles=["system"])
@log_info_record(LOG_ACTIONS["MOD"])
def role_update(role, identity, role_id):
    """
    role更新
    """
    data = request.get_json()

    role_name = data.get("role_name")
    role_memo = data.get("role_memo")

    try:
        pre_sql = Roles.query.filter(Roles.role_id == role_id)

        if pre_sql.first() is None:
            return jsonify(operation_res_build(f"role_id: { role_id } does not exist", False)), False

        pre_sql.update({"role_name": role_name, "role_memo": role_memo})
        db.session.commit()
    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "a error happened in deletion")
        logger.exception(e)
        return jsonify(operation_res_build("a error happened in deletion", False)), False

    return jsonify(operation_res_build("deletion ok", True)), True


@roles_bp.route("/<int:role_id>", methods=["DELETE"])
@role_auth_require(auth_roles=["system"])
@log_info_record(LOG_ACTIONS["DEL"])
def role_delete(role, identity, role_id):
    """
    role删除
    """
    try:
        if role_id == 1:
            return jsonify(operation_res_build("system manager is not allowed to be deleted", False)), False

        db.session.delete(Roles.query.filter(Roles.role_id == role_id).first())
        db.session.commit()
    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "a error happened in deletion")
        logger.exception(e)
        return jsonify(operation_res_build("a error happened in deletion", False)), False

    return jsonify(operation_res_build("deletion ok", True)), True
