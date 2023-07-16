from flask import Blueprint, jsonify, request

from models.mursModel import db, Murs

from schema.modelSchema import murs_schema, murs_schema_single, menus_schema_single

from auth.identityAuth import role_auth_require
from auth.msgDef import MENU_INFO
from utils.tool import operation_res_build
from utils.log import log_info_record, LOG_ACTIONS
import logger

murs_bp = Blueprint("murs", __name__, url_prefix="/api/murs")


@murs_bp.route("/", methods=["GET"])
@role_auth_require(grant_all=True)
def mur_request_by_id(role, identity):
    """
    mur信息获取，根据ur_id
    """
    try:
        ur_id = request.args.get("ur_id")

        murs = Murs.query.filter(Murs.ur_id == (identity["ur_id"] if ur_id is None else int(ur_id))).all()
        rets = []

        _ = [murs_schema_single.dump(mur) for mur in murs]
        __ = [(mur_, MENU_INFO[mur_["menu_id"]]) for mur_ in _]

        # 分两次写是为了避免二级菜单出现但是父菜单还未写入
        for mur_, menu_ in __:
            # 一级菜单写入
            if mur_["mur_state"] and menu_["parent_menu_id"] is None:
                rets.append({"menu_id": mur_["menu_id"], "menu_name": menu_["menu_name"],
                            "menu_memo": menu_["menu_memo"], "menu_path": menu_["menu_path"],
                             "menu_icon": menu_["menu_icon"], "menu_mpath": menu_["menu_mpath"], "children": []})

        for mur_, menu_ in __:
            # 二级菜单写入
            if mur_["mur_state"] and menu_["parent_menu_id"] is not None:
                for ret in rets:
                    if ret["menu_id"] == menu_["parent_menu_id"]:
                        ret["children"].append({"menu_id": mur_["menu_id"], "menu_name": menu_["menu_name"],
                                                "menu_memo": menu_["menu_memo"], "menu_path": menu_["menu_path"],
                                                "menu_icon": menu_["menu_icon"], "menu_mpath": menu_["menu_mpath"]})
    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "load mur failed")
        logger.exception(e)
        return jsonify(operation_res_build("load mur failed", False))

    return jsonify(operation_res_build("load mur ok", True, data=rets))


@murs_bp.route("/", methods=["POST"])
@role_auth_require(auth_roles=["system"])
@log_info_record(LOG_ACTIONS["ADD"])
def mur_add(role, identity):
    """
    给单位角色添加菜单
    :param role:
    :param identity:
    :return:
    """
    data = request.get_json()

    ur_id = data.get("ur_id")
    menu_active_ls = data.get("menu_active_ls")
    menu_inactive_ls = data.get("menu_inactive_ls")

    try:
        # 读取当前ur的菜单配置
        murs = Murs.query.filter(Murs.ur_id == ur_id).all()
        murs_ = murs_schema.dump(murs)
        menu_ids = [x["menu_id"] for x in murs_]

        # 生成添加组、修改组
        add_mur_ls = []
        update_mur_ls = []

        for k in menu_active_ls:
            if k not in menu_ids:
                add_mur_ls.append(k)
            else:
                update_mur_ls.append((k, True))

        for k in menu_inactive_ls:
            if k in menu_ids:
                update_mur_ls.append((k, False))

        for i in add_mur_ls:
            db.session.add(Murs(i, ur_id, True, ''))

        for i in update_mur_ls:
            Murs.query.filter(Murs.menu_id == i[0], Murs.ur_id == ur_id).update({"mur_state": i[1]})

        db.session.commit()
    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "add mur fail")
        logger.exception(e)
        return jsonify(operation_res_build("add mur fail", False)), False

    return jsonify(operation_res_build("add mur ok", True)), True


@murs_bp.route("/", methods=["PUT"])
@role_auth_require(auth_roles=["system"])
@log_info_record(LOG_ACTIONS["MOD"])
def mur_request_active(role, identity):
    """
    mur激活或禁用
    """
    data = request.get_json()

    mur_id = data.get("mur_id")
    active = data.get("active")

    try:
        db.session.query.filter(Murs.mur_id == mur_id).update({"mur_state": active == '1'})
        db.session.commit()
    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "update mur failed")
        logger.exception(e)
        return jsonify(operation_res_build("update mur failed", False)), False

    return jsonify(operation_res_build("update mur ok", True)), True



