from flask import Blueprint, jsonify, request, current_app

from models.unitsAppTypesModel import db, UnitsApptypes
from schema.modelSchema import units_app_types_schema_single, units_app_types_schema, app_types_schema_single
from models.unitsModel import Units
from models.apptypesModel import AppTypes

from utils.tool import operation_res_build, get_current_time
from utils.log import LOG_ACTIONS, log_info_record

import logger
from auth.identityAuth import role_auth_require

units_app_types_bp = Blueprint("units_app_types", __name__, url_prefix="/api/unit_app_types")


@units_app_types_bp.route("/<int:unit_id>", methods=["GET"])
@role_auth_require(grant_all=True)
def units_app_types_request(role, identity, unit_id):
    """
    unit_app信息获取
    """
    try:
        units_app_types = UnitsApptypes.query.filter(UnitsApptypes.unit_id == unit_id).all()

        ret = []
        for _ in units_app_types:
            ua = units_app_types_schema_single.dump(_)

            if ua["ua_state"]:
                at = app_types_schema_single.dump(_.type)

                tmp = {}
                tmp.update(ua)
                tmp.update(at)

                ret.append(tmp)

    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "load unitsApptypes failed")
        logger.exception(e)
        return jsonify(operation_res_build("load unitsApptypes failed", False))

    return jsonify(operation_res_build("load unitsApptypes ok", True, data=ret))


@units_app_types_bp.route("/<int:unit_id>", methods=["PUT"])
@role_auth_require(auth_roles=["system"])
@log_info_record(LOG_ACTIONS["MOD"])
def units_app_types_update(role, identity, unit_id):
    """
    ur更新
    """
    data = request.get_json()

    ua_active_ls = data.get("added")
    ua_inactive_ls = data.get("reduced")

    try:
        unit = Units.query.filter(Units.unit_id == unit_id).first()

        if unit is None:
            return jsonify(operation_res_build(f"公司unit_id { unit_id }不存在", False)), False

        uas = UnitsApptypes.query.filter(UnitsApptypes.unit_id == unit_id).all()
        uas_ = units_app_types_schema.dump(uas)

        type_ids = [x["type_id"] for x in uas_]

        # 生成添加组、修改组
        add_ua_ls = []
        update_ua_ls = []

        for type_id in ua_active_ls:
            if type_id not in type_ids:
                add_ua_ls.append(type_id)
            else:
                update_ua_ls.append((type_id, True))

        for type_id in ua_inactive_ls:
            if type_id in type_ids:
                update_ua_ls.append((type_id, False))

        for i in add_ua_ls:
            db.session.add(UnitsApptypes(unit_id, i, None, True, None))

        for i in update_ua_ls:
            UnitsApptypes.query.filter(UnitsApptypes.type_id == i[0], UnitsApptypes.unit_id == unit_id).update({"ua_state": i[1]})

        db.session.commit()
    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "a error happened in update")
        logger.exception(e)
        return jsonify(operation_res_build("a error happened in update", False)), False

    return jsonify(operation_res_build("update ok", True)), True


# @units_app_types_bp.route("/<int:ua_id>", methods=["GET"])
# @role_auth_require(grant_all=True)
# def units_app_types_request_by_id(role, identity, ua_id):
#     """
#     unit_app信息获取，根据ua_id
#     """
#     try:
#         if role == "system":
#             units_app_types = UnitsApptypes.query.filter(UnitsApptypes.ua_id == ua_id).first()
#         else:
#             units_app_types = UnitsApptypes.query.filter(UnitsApptypes.ua_id == ua_id,
#                                                          UnitsApptypes.unit_id == identity["unit_id"]).first()
#
#         if units_app_types is None:
#             return jsonify(operation_res_build("unitsAppTypes does not exist", False))
#     except Exception as e:
#         logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "load unitsAppTypes failed")
#         logger.exception(e)
#         return jsonify(operation_res_build("load unitsAppTypes failed", False))
#
#     return jsonify(
#         operation_res_build("load unitsAppTypes ok", True,
#                             data=units_app_types_schema.dump(units_app_types)))


@units_app_types_bp.route("/", methods=["POST"])
@role_auth_require(auth_roles=["system", "unit_manager"])
@log_info_record(LOG_ACTIONS["ADD"])
def units_app_types_add(role, identity):
    """
    unit_app添加
    """
    data = request.get_json()

    unit_id = identity["unit_id"]
    type_id = data.get("type_id")
    ua_template = data.get("ua_template")
    ua_state = data.get("ua_state")
    ua_memo = data.get("ua_memo")

    try:
        at = AppTypes.query.filter(AppTypes.type_id == type_id).first()
        if at is None:
            return jsonify(operation_res_build(f"type_id: { type_id } exist", False)), False

        ua = UnitsApptypes.query.filter(UnitsApptypes.unit_id == unit_id if role != "system" else True,
                                        UnitsApptypes.type_id == type_id).first()

        if ua is not None:
            return jsonify(operation_res_build("unitsAppTypes exist", False)), False

        db.session.add(UnitsApptypes(unit_id, type_id, ua_template, ua_state, ua_memo))
        db.session.commit()
    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "a error happened in addition")
        logger.exception(e)
        return jsonify(operation_res_build("a error happened in addition", False)), False

    return jsonify(operation_res_build("addition ok", True)), True


# @units_app_types_bp.route("/<int:ua_id>", methods=["PUT"])
# @role_auth_require(auth_roles=["system", "unit_manager"])
# @log_info_record(LOG_ACTIONS["MOD"])
# def units_app_types_update(role, identity, ua_id):
#     """
#     unit_app更新
#     """
#
#     data = request.get_json()
#
#     unit_id = identity["unit_id"]
#     type_id = data.get("type_id")
#     ua_template = data.get("ua_template")
#     ua_state = data.get("ua_state")
#     ua_memo = data.get("ua_memo")
#
#     try:
#         if role == "system":
#             pre_sql = UnitsApptypes.query.filter(UnitsApptypes.ua_id == ua_id)
#         else:
#             pre_sql = UnitsApptypes.query.filter(UnitsApptypes.ua_id == ua_id,
#                                                  UnitsApptypes.unit_id == unit_id)
#         if pre_sql.first is None:
#             return jsonify(operation_res_build("the role does not exist", False)), False
#
#         pre_sql.update({"unit_id": unit_id, "type_id": type_id, "ua_template": ua_template, "ua_state": ua_state,
#                         "ua_memo": ua_memo})
#         db.session.commit()
#     except Exception as e:
#         logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "a error happened in update")
#         logger.exception(e)
#         return jsonify(operation_res_build("a error happened in update", False)), False
#
#     return jsonify(operation_res_build("update ok", True)), False
