from flask import Blueprint, jsonify, request, current_app

from models.uursModel import db, Uurs
from models.usersModel import Users
from schema.modelSchema import uurs_schema_single, users_schema_single

from utils.tool import operation_res_build, get_current_time, usr_psw_generator
from utils.log import log_info_record, LOG_ACTIONS
from auth.identityAuth import role_auth_require, expired_token_require, identity_confirm_token_generate, \
    identity_access_token_refresh, field_check_unit
from auth.msgDef import FIELD_CODE
import logger

uurs_bp = Blueprint("uurs", __name__, url_prefix="/api/uurs")


@uurs_bp.route("/", methods=["POST"])
@role_auth_require(auth_roles=["system", "unit_manager"])
@log_info_record(LOG_ACTIONS["ADD"])
def uur_add(role, identity):
    """
    uur添加，若user不存在会被创建
    """
    data = request.get_json()
    ur_id = data.get("ur_id")
    unit_id_copy = data.get("unit_id")
    mobile = data.get("mobile")

    user = Users.query.filter(Users.mobile == mobile).first()

    if user is None:
        name = data.get("name")
        passwd = usr_psw_generator(data.get("passwd"))
        user_state = current_app.config["USER_STATE_DEFAULT"]
        user_memo = data.get("user_memo")
        user_mail = data.get("user_mail")

        user_new = Users(mobile, name, passwd, user_state, user_memo, user_mail)

        db.session.add(user_new)
        db.session.flush()
        u_id = user_new.u_id

        db.session.commit()
    else:
        user_ = users_schema_single.dump(user)
        u_id = user_["u_id"]

    # 查出这个用户存在于本单位中
    pre_sql = Uurs.query.filter(Uurs.u_id == u_id, Uurs.unit_id_copy == unit_id_copy)
    uur = pre_sql.first()
    if uur is not None:
        uur_ = uurs_schema_single.dump(uur)
        if uur_["uur_state"]:
            return jsonify(operation_res_build("该用户已存在，需操作请去修改", False)), False
        else:
            pre_sql.update({"uur_state": 1})
            db.session.commit()
            return jsonify(operation_res_build("已激活该用户", False)), False

    uur_state = current_app.config["UUR_STATE_DEFAULT"]
    uur_time = get_current_time()
    uur_memo = data.get("uur_memo")

    db.session.add(Uurs(ur_id, u_id, unit_id_copy, uur_state, uur_time, uur_memo))
    db.session.commit()

    return jsonify(operation_res_build("add ok", True)), False


@uurs_bp.route("/<int:uur_id>", methods=["PATCH"])
@role_auth_require(auth_roles=["system", "unit_manager"])
@log_info_record(LOG_ACTIONS["MOD"])
def uur_active(role, identity, uur_id):
    """
        删除 uur
        :param role:
        :param identity:
        :param uur_id: 删除的uur_id 前端传
        :return:
    """

    try:
        pre_sql = Uurs.query.filter(Uurs.uur_id == uur_id)
        uur = pre_sql.first()
        if uur is None:
            return jsonify(operation_res_build("uur_id does not exist", False)), False

        uur_ = uurs_schema_single.dump(uur)

        if uur_["uur_id"] == identity["uur_id"]:
            return jsonify(operation_res_build("you can not inactive yourself", False)), False

        # u_id = uur_["u_id"]
        # 只保留一个uur是激活状态
        # Uurs.query.filter(u_id == Uurs.u_id, uur_id != Uurs.uur_id).update({"uur_state": 0})
        pre_sql.update({"uur_state": 0})

        db.session.commit()
    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "a error happened in operation")
        logger.exception(e)
        return jsonify(operation_res_build("a error happened in operation", False)), False

    return jsonify(operation_res_build("operation ok", True)), True


@uurs_bp.route("/refresh", methods=["GET"])
@expired_token_require
def uur_token_refresh(to_refresh, identity):
    """
    uur令牌刷新
    """
    if not to_refresh:
        return jsonify(operation_res_build("refresh token invalid, plz login", False))

    access_token = identity_confirm_token_generate(uur_id=identity["uur_id"], role_id=identity["role_id"],
                                                   ur_id=identity["ur_id"],
                                                   u_id=identity["u_id"], name=identity["name"],
                                                   unit_id=identity["unit_id"])

    refresh_token = identity_access_token_refresh(uur_id=identity["uur_id"], role_id=identity["role_id"],
                                                  ur_id=identity["ur_id"],
                                                  u_id=identity["u_id"], name=identity["name"],
                                                  unit_id=identity["unit_id"])

    return jsonify(operation_res_build("token refresh ok", True,
                                       data={"access_token": access_token, "refresh_token": refresh_token}))


@uurs_bp.route("/<uur_id>", methods=["PUT"])
@role_auth_require(auth_roles=["system", "unit_manager"])
@log_info_record(LOG_ACTIONS["MOD"])
def uur_update(role, identity, uur_id):
    """
      uur更新，若更新的ur与u的组合不存在则创建
    :param role:
    :param identity:
    :param uur_id:
    :return:
    """
    data = request.get_json()

    ur_id = data.get("ur_id")
    unit_id_copy = data.get("unit_id")
    mobile = data.get("mobile")
    user_mail = data.get("user_mail")
    name = data.get("name")
    uur_memo = data.get("uur_memo")
    # 水平检测
    if (rc := field_check_unit(role, unit_id_copy, identity["unit_id"])) != FIELD_CODE["PASS"]:
        return jsonify(operation_res_build("filed check fail", False, errCode=rc)), False

    try:
        pre_sql_uur_sender = Uurs.query.filter(Uurs.uur_id == uur_id)
        uur_sender = pre_sql_uur_sender.first()

        if uur_sender is None:
            return jsonify(operation_res_build(f"uur {uur_id} you provided is not existed", False)), False

        uur_sender_ = uurs_schema_single.dump(uur_sender)

        user_sender = uur_sender.u
        user_sender_ = users_schema_single.dump(user_sender)

        if user_sender_["mobile"] != mobile:
            # 电话被改动
            user_new = Users.query.filter(Users.mobile == mobile).first()

            if user_new is not None:
                return jsonify(operation_res_build(f"这个 {mobile}已被别人使用！", False)), False

        if uur_sender_["ur_id"] != ur_id:
            # 说明改变了职位
            pre_sql_uur_sender.update({"uur_state": 0})

            pre_sql_uur = Uurs.query.filter(Uurs.ur_id == ur_id, Uurs.u_id == user_sender_["u_id"])

            if pre_sql_uur.first() is None:
                db.session.add(Uurs(ur_id, user_sender_["u_id"], unit_id_copy,
                                    current_app.config["UUR_STATE_DEFAULT"], get_current_time(), uur_memo))
            else:
                pre_sql_uur.update({"uur_state": 1})
        else:
            if uur_sender_["uur_memo"] != uur_memo:
                pre_sql_uur_sender.update({"uur_memo": uur_memo})

        Users.query.filter(Users.u_id == uur_sender_["u_id"]).update({
            "name": name, "mobile": mobile, "user_mail": user_mail
        })
        db.session.commit()
    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "a error happened in update")
        logger.exception(e)
        return jsonify(operation_res_build("a error happened in update", False)), False

    return jsonify(operation_res_build("uur update ok", True)), True
