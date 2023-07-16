from flask import Blueprint, jsonify, request

from models.menusModel import db, Menus
from schema.modelSchema import menus_schema

from utils.tool import operation_res_build
from utils.log import log_info_record, LOG_ACTIONS

from auth.identityAuth import role_auth_require
import logger

menus_bp = Blueprint("menus", __name__, url_prefix="/api/menus")


@menus_bp.route("/", methods=["GET"])
@role_auth_require(grant_all=["system"])
def menus_request(role, identity):
    """
    获取所有菜单
    :param role:
    :param identity:
    :return:
    """
    try:
        menus = menus_schema.dump(Menus.query.all())

        menu = []
        if not len(menus):
            return jsonify(operation_res_build("load menus does not exist", False))

        for menu_ in menus:
            if menu_["parent_menu_id"] is None:
                menu.append({"menu_id": menu_["menu_id"], "menu_name": menu_["menu_name"],
                             "menu_memo": menu_["menu_memo"], "menu_path": menu_["menu_path"],
                             "menu_mpath": menu_["menu_mpath"],
                             "menu_icon": menu_["menu_icon"], "children": []})
        for menu_ in menus:
            if menu_["parent_menu_id"] is not None:
                for child in menu:
                    if child["menu_id"] == menu_["parent_menu_id"]:
                        child["children"].append({"menu_id": menu_["menu_id"], "menu_name": menu_["menu_name"],
                                                  "menu_memo": menu_["menu_memo"], "menu_path": menu_["menu_path"],
                                                  "menu_mpath": menu_["menu_mpath"],
                                                  "menu_icon": menu_["menu_icon"], "parent_menu_id": menu_["parent_menu_id"]})
    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "load menus failed")
        logger.exception(e)
        return jsonify(operation_res_build("load menus failed", False))

    return jsonify(operation_res_build("load menus ok", True, data=menu))


@menus_bp.route("/", methods=["POST"])
@role_auth_require(auth_roles=["system"])
@log_info_record(LOG_ACTIONS["ADD"])
def menu_request_add(role, identity):
    """
    添加menu
    :param role:
    :param identity:
    :return:
    """
    data = request.get_json()

    parent_menu_id = data.get("parent_menu_id")
    menu_name = data.get("menu_name")
    menu_memo = data.get("menu_memo")
    menu_path = data.get("menu_path")
    menu_mpath = data.get("menu_mpath")
    menu_icon = data.get("menu_icon")

    try:
        db.session.add(Menus(parent_menu_id, menu_name, menu_memo, menu_path, menu_mpath, menu_icon))
        db.session.commit()
    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "menu add fail")
        logger.exception(e)
        return jsonify(operation_res_build("menu add fail", False)), False

    return jsonify(operation_res_build("menu add ok", True)), True


@menus_bp.route("/<int:menu_id>", methods=["DELETE"])
@role_auth_require(auth_roles=["system"])
@log_info_record(LOG_ACTIONS["DEL"])
def menu_request_del(role, identity, menu_id):
    """
    通过menu_id 删除menu
    :param role:
    :param identity:
    :param menu_id:
    :return:
    """
    try:
        db.session.delete(Menus.query.filter(Menus.menu_id == menu_id).first())
        db.session.commit()
    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "delete menu failed")
        logger.exception(e)
        return jsonify(operation_res_build("delete menu failed", False)), False
    return jsonify(operation_res_build("delete menu ok", True)), True


@menus_bp.route("/<int:menu_id>", methods=["PUT"])
@role_auth_require(auth_roles=["system"])
@log_info_record(LOG_ACTIONS["MOD"])
def menu_request_update(role, identity, menu_id):
    """
    修改menu
    :param role:
    :param identity:
    :param menu_id:
    :return:
    """
    data = request.get_json()

    parent_menu_id = data.get("parent_menu_id")
    menu_name = data.get("menu_name")
    menu_memo = data.get("menu_memo")
    menu_path = data.get("menu_path")
    menu_icon = data.get("menu_icon")
    menu_mpath = data.get("menu_mpath")

    try:
        pre_sql = Menus.query.filter(menu_id == Menus.menu_id)
        if pre_sql.first() is None:
            return jsonify(operation_res_build(" menu does not exist", False)), False
        else:
            pre_sql.update({"menu_name": menu_name, "parent_menu_id": parent_menu_id, "menu_memo": menu_memo,
                            "menu_path": menu_path, "menu_icon": menu_icon, "menu_mpath": menu_mpath})

        db.session.commit()
    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "update menu failed")
        logger.exception(e)
        return jsonify(operation_res_build("update menu failed", False)), False

    return jsonify(operation_res_build("update menu ok", True)), True
