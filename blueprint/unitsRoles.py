from flask import Blueprint, jsonify, request, current_app

from models.unitsRolesModel import db, UnitsRoles
from models.rolesModel import Roles
from models.unitsModel import Units
from schema.modelSchema import units_roles_schema, units_roles_schema_single, units_schema_single

from utils.tool import operation_res_build, get_current_time
from utils.log import log_info_record, LOG_ACTIONS

from auth.identityAuth import role_auth_require, field_check_unit, FIELD_CODE
from auth.msgDef import ROLE_ID_ROLE_NAME_REFLECTION, ROLE_ID_ROLE_MEMO_REFLECTION
import logger

from sqlalchemy import func

units_roles_bp = Blueprint("units_roles", __name__, url_prefix="/api/units_roles")


@units_roles_bp.route("/unit/<int:unit_id>", methods=["GET"])
@role_auth_require(grant_all=True)
def units_roles_request_by_unit(role, identity, unit_id):
    """
    ur信息获取，根据unit_id
    :param role:
    :param identity:
    :param unit_id:
    :return:
    """

    ret = []
    try:
        # 水平检测
        if (rc := field_check_unit(role, unit_id, identity["unit_id"])) != FIELD_CODE["PASS"]:
            return jsonify(operation_res_build("filed check fail", False, errCode=rc)), False
        # 通过unit_id查询到公司下所有已激活的角色
        units_roles = UnitsRoles.query.filter(UnitsRoles.role_id == Roles.role_id, UnitsRoles.unit_id == unit_id, UnitsRoles.ur_state == "1").all()
        # 遍历添加到数组
        for _ in units_roles:
            ur_ = units_roles_schema_single.dump(_)

            ret.append({
                "role_id": ur_["role_id"],
                "role_name": ROLE_ID_ROLE_NAME_REFLECTION[ur_["role_id"]],
                "role_memo": ROLE_ID_ROLE_MEMO_REFLECTION[ur_["role_id"]],
                "ur_id": ur_["ur_id"],
                "ur_memo": ur_["ur_memo"]
            })
    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "load units_role failed")
        logger.exception(e)
        return jsonify(operation_res_build("load units_role failed", False))

    return jsonify(operation_res_build("load units_role ok", True, data=ret))


@units_roles_bp.route("/<int:unit_id>", methods=["PUT"])
@role_auth_require(auth_roles=["system"])
@log_info_record(LOG_ACTIONS["MOD"])
def units_role_update(role, identity, unit_id):
    """
    添加或者去激活公司角色
    :param role:
    :param identity:
    :param unit_id:
    :return:
    """
    data = request.get_json()

    role_active_ls = data.get("added")
    role_inactive_ls = data.get("reduced")

    try:

        unit = Units.query.filter(Units.unit_id == unit_id).first()

        if unit is None:
            return jsonify(operation_res_build(f"公司unit_id { unit_id }不存在", False)), False

        unit_name_copy = units_schema_single.dump(unit)["unit_name"]
        urs = UnitsRoles.query.filter(UnitsRoles.unit_id == unit_id).all()
        urs_ = units_roles_schema.dump(urs)
        # 该公司所有的role_id
        role_ids = [x["role_id"] for x in urs_]

        # 生成添加组、修改组
        add_ur_ls = []
        update_ur_ls = []

        for role_id in role_active_ls:
            # 在添加组且在数据库无纪录、就添加到add_ur_ls
            if role_id not in role_ids:
                add_ur_ls.append(role_id)
            else:
                # 在数据库中存在
                update_ur_ls.append((role_id, True))

        for role_id in role_inactive_ls:
            if role_id in role_ids:
                update_ur_ls.append((role_id, False))

        for i in add_ur_ls:
            db.session.add(UnitsRoles(unit_id, i, True, get_current_time(), unit_name_copy,
                                      ROLE_ID_ROLE_MEMO_REFLECTION[i], None))

        for i in update_ur_ls:
            UnitsRoles.query.filter(UnitsRoles.role_id == i[0], UnitsRoles.unit_id == unit_id).update({"ur_state": i[1]})

        db.session.commit()
    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "a error happened in update")
        logger.exception(e)
        return jsonify(operation_res_build("a error happened in update", False)), False

    return jsonify(operation_res_build("update ok", True)), True
