from flask import Blueprint, jsonify, request
from sqlalchemy import func

from auth.msgDef import FIELD_CODE
from models.rentsModel import Rents, db
from schema.modelSchema import rents_schema, rents_schema_single
from utils.tool import operation_res_build, get_current_time
from utils.log import log_info_record, LOG_ACTIONS

import logger
from auth.identityAuth import role_auth_require, field_check_unit

rents_bp = Blueprint("rents", __name__, url_prefix="/api/rents")


@rents_bp.route("/", methods=["GET"])
@role_auth_require(auth_roles=["system"])
def rents_request(role, identity):
    try:
        rents = Rents.query.all()

        total = db.session.query(func.count(Rents.rent_id)).scalar()

    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "load rents failed")
        logger.exception(e)
        return jsonify(operation_res_build("load rents failed", False))

    return jsonify(operation_res_build("load rents ok", True, data={"rent":rents_schema.dump(rents), "total":total}))


@rents_bp.route("/<int:unit_id>", methods=["GET"])
@role_auth_require(auth_roles=["system", "unit_manager"])
def rent_request_by_unitId(role, identity, unit_id):
    try:
        # 水平检测
        if (rc := field_check_unit(role, unit_id, identity["unit_id"])) != FIELD_CODE["PASS"]:
            return jsonify(operation_res_build("filed check fail", False, errCode=rc)), False
        rent = Rents.query.filter(Rents.unit_id == unit_id).first()
        if rent is None:
            return jsonify(operation_res_build("load rent is not exist", False))
    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "load rent failed")
        logger.exception(e)
        return jsonify(operation_res_build("load rent failed", False))

    return jsonify(operation_res_build("load rent ok", True, data={"rent":rents_schema_single.dump(rent)}))


@rents_bp.route("/", methods=["POST"])
@role_auth_require(auth_roles=["system"])
@log_info_record(LOG_ACTIONS["ADD"])
def rent_add(role, identity):
    """
    添加租户
    :param role:
    :param identity:
    :return:
    """
    data = request.get_json()

    unit_id = data.get("unit_id")

    rent_time = get_current_time()
    rent_length = data.get("rent_length")
    rent_value = data.get("rent_value")
    rent_memo = data.get("rent_memo")
    try:
        if len(Rents.query.filter(Rents.unit_id == unit_id).all()):
            return jsonify(operation_res_build("the unit exist", False)), False

        db.session.add(Rents(unit_id, rent_time, rent_length, rent_value, rent_memo))
        db.session.commit()
    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "a error happened in addition")
        logger.exception(e)
        return jsonify(operation_res_build("a error happened in addition", False)), False

    return jsonify(operation_res_build("addition ok", True)), True



@rents_bp.route("/<int:rent_id>", methods=["DELETE"])
@role_auth_require(auth_roles=["system"])
@log_info_record(LOG_ACTIONS["DEL"])
def rent_delete(role, identity, rent_id):
    """
     删除租户
    :param role:
    :param identity:
    :param rent_id:
    :return:
    """
    try:
        rent = Rents.query.filter(Rents.rent_id == rent_id).first()

        if rent is not None:
            db.session.delete(rent)
            db.session.commit()
    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "a error happened in deletion")
        logger.exception(e)
        return jsonify(operation_res_build("a error happened in deletion", False)), False

    return jsonify(operation_res_build("deletion ok", True)), True


@rents_bp.route("/<int:rent_id>", methods=["PUT"])
@role_auth_require(auth_roles=["system"])
@log_info_record(LOG_ACTIONS["MOD"])
def rent_update(role, identity, rent_id):
    """
    修改租户信息
    :param role:
    :param identity:
    :param rent_id:
    :return:
    """
    data = request.get_json()

    unit_id = data.get("unit_id")
    rent_time = data.get("rent_time")
    rent_value = data.get("rent_value")
    rent_expiretime = data.get("rent_expiretime")
    rent_memo = data.get("rent_memo")

    try:
        if not len(Rents.query.filter(Rents.rent_id == rent_id).all()):
            return jsonify(operation_res_build("the rent does not exist", False)), False

        Rents.query.filter(Rents.rent_id == rent_id).update({"unit_id": unit_id, "rent_time": rent_time,
                                                             "rent_value": rent_value, "rent_memo": rent_memo,
                                                             "rent_expiretime": rent_expiretime})
        db.session.commit()
    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "a error happened in update")
        logger.exception(e)
        return jsonify(operation_res_build("a error happened in update", False)), False

    return jsonify(operation_res_build("update ok", True)), True
