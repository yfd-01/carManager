from flask import Blueprint, jsonify, request, current_app, session
from models.unitsModel import db, Units

from schema.modelSchema import units_schema, units_schema_single
from utils.tool import operation_res_build, get_current_time
from utils.log import LOG_ACTIONS, log_info_record

import logger
from auth.identityAuth import role_auth_require

units_bp = Blueprint("units", __name__, url_prefix="/api/units")


def __unit_tree_assemble(units_, pid=''):
    if not pid:
        ls = []
        # 添加父节点
        for item in [unit for unit in units_ if not unit["parent_unit_id"]]:
            item["children"] = __unit_tree_assemble(units_, item["unit_id"])
            ls.append(item)

        return ls
    else:
        ls = []

        for item in [unit for unit in units_ if unit["parent_unit_id"] == pid]:
            item["children"] = __unit_tree_assemble(units_, item["unit_id"])
            ls.append(item)

        return ls


def __trim_tree(identity_id, ls):
    for i in ls:
        if i["unit_id"] == identity_id:
            return [i]

        if len(i["children"]):
            ret = __trim_tree(identity_id, i["children"])

            if len(ret):
                return ret

    return []


@units_bp.route("/", methods=["GET"])
@role_auth_require(grant_all=True)
def units_request(role, identity):
    """
        unit信息获取
    """
    try:
        units = Units.query.all()
        units_ = units_schema.dump(units)
    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "load units failed")
        logger.exception(e)
        return jsonify(operation_res_build("load units failed", False))
    # 树形菜单
    units_tree = __unit_tree_assemble(units_)
    if role != "system":
        units_tree = __trim_tree(identity["unit_id"], units_tree)

    return jsonify(operation_res_build("load units ok", True, data={"units": units_tree}))


@units_bp.route("/<int:unit_id>", methods=["GET"])
@role_auth_require(grant_all=True)
def unit_request_by_id(role, identity, unit_id):
    """
    unit信息获取，根据unit_id
    """
    try:
        unit = Units.query.filter(Units.unit_id == unit_id,
                                  (Units.unit_id == identity["unit_id"]) if role != "system" else True).first()

        if unit is None:
            return jsonify(operation_res_build("load unit is not exist", False))
    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "load unit failed")
        logger.exception(e)
        return jsonify(operation_res_build("load unit failed", False))

    return jsonify(operation_res_build("load unit ok", True, data={"unit": units_schema_single.dump(unit)}))


@units_bp.route("/", methods=["POST"])
@role_auth_require(auth_roles=["system", "unit_manager"])
@log_info_record(LOG_ACTIONS["ADD"])
def unit_add(role, identity):
    """
    添加公司
    :param role:
    :param identity:
    :return:
    """

    data = request.get_json()
    parent_unit_id = data.get("parent_unit_id")
    # 不是系统管理员只能添加子公司
    if parent_unit_id == "" and role != "system":
        return jsonify(operation_res_build("authority error", False)), False
    unit_name = data.get("unit_name")
    unit_address = data.get("unit_address")
    unit_contact = data.get("unit_contact")
    unit_tel = data.get("unit_tel")
    unit_regtime = get_current_time()
    unit_state = current_app.config["UNIT_STATE_DEFAULT"]
    unit_memo = data.get("unit_memo")
    rent_expiretime = data.get("rent_expiretime")

    # 如果rent_expiretime是空就查父公司的rent_expiretime
    if rent_expiretime == "" or rent_expiretime is None:
        # 查父节点
        unit_ = units_schema_single.dump(Units.query.filter(Units.unit_id == parent_unit_id).first())
        rent_expiretime = unit_["rent_expiretime"]

    try:
        if len(Units.query.filter(Units.unit_name == unit_name).all()):
            return jsonify(operation_res_build("the unit exist", False)), False
        db.session.add(Units(parent_unit_id, unit_name, unit_address, unit_contact, unit_tel, rent_expiretime,
                             unit_regtime, unit_state, unit_memo))
        db.session.commit()
    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "a error happened in addition")
        logger.exception(e)
        return jsonify(operation_res_build("a error happened in addition", False)), False

    return jsonify(operation_res_build("addition ok", True)), True


@units_bp.route("/<int:unit_id>", methods=["PUT"])
@role_auth_require(auth_roles=["system", "unit_manager"])
@log_info_record(LOG_ACTIONS["MOD"])
def unit_update(role, identity, unit_id):
    """
    修改公司信息
    :param role:
    :param identity:
    :param unit_id:
    :return:
    """
    data = request.get_json()
    unit_name = data.get("unit_name")
    unit_address = data.get("unit_address")
    unit_contact = data.get("unit_contact")
    unit_tel = data.get("unit_tel")
    unit_state = True if data.get("unit_state") == 1 else False
    unit_memo = data.get("unit_memo")
    rent_expiretime = data.get("rent_expiretime")

    try:

        if not len(Units.query.filter(Units.unit_id == unit_id).all()):
            return jsonify(operation_res_build("the unit does not exist", False)), False
        if rent_expiretime == "" or rent_expiretime is None:
            Units.query.filter(Units.unit_id == unit_id).update({
                "unit_name": unit_name,
                "unit_address": unit_address,
                "unit_contact": unit_contact,
                "unit_tel": unit_tel,
                "unit_state": unit_state,
                "unit_memo": unit_memo})
            db.session.commit()
        else:
            Units.query.filter(Units.unit_id == unit_id).update({
                "unit_name": unit_name,
                "unit_address": unit_address,
                "unit_contact": unit_contact,
                "unit_tel": unit_tel,
                "rent_expiretime": rent_expiretime,
                "unit_state": unit_state,
                "unit_memo": unit_memo})
            db.session.commit()
    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "a error happened in update")
        logger.exception(e)
        return jsonify(operation_res_build("a error happened in update", False)), False

    return jsonify(operation_res_build("update ok", True)), True
