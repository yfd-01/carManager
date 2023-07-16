from flask import Blueprint, jsonify, request, current_app, session
from models.usersModel import db, Users
from models.unitsRolesModel import UnitsRoles
from models.uursModel import Uurs
from models.unitsModel import Units
from schema.modelSchema import users_schema_single, uurs_schema, units_roles_schema_single,\
    units_schema_single, uurs_schema_single

from sqlalchemy import func
from auth.identityAuth import role_auth_require, first_login_require, identity_choose_token_generate, \
    identity_confirm_token_generate, identity_access_token_refresh
from auth.msgDef import ROLE_ID_ROLE_NAME_REFLECTION, ROLE_ID_ROLE_MEMO_REFLECTION, ROLE_NAME_ROLE_ID_REFLECTION

from utils.tool import operation_res_build, usr_psw_generator, random_chars_gen, get_time_offset, get_time_gap, get_current_time
from utils.log import log_info_record, LOG_ACTIONS
from utils.mail import send_mail
import logger

users_bp = Blueprint("users", __name__, url_prefix="/api/users")


@users_bp.route("/user_token_unpack", methods=["GET"])
@role_auth_require(grant_all=True)
def token_info_unpack(role, identity):
    try:
        user = Users.query.filter(Users.u_id == identity["u_id"]).first()

        if user is None:
            raise Exception

        user_ = users_schema_single.dump(user)
        if not user_["user_state"]:
            return jsonify(operation_res_build("user state is inactive", False))

        unit_name = units_schema_single.dump(Units.query.filter(Units.unit_id == identity["unit_id"]).first())["unit_name"]

        rets = {}
        rets.update(user_)
        rets["role"] = role
        rets["role_id"] = ROLE_NAME_ROLE_ID_REFLECTION[role]
        rets["role_memo"] = ROLE_ID_ROLE_MEMO_REFLECTION[identity["role_id"]]
        rets["unit_id"] = identity["unit_id"]
        rets["unit_name"] = unit_name

        del rets["findpass_duetime"]
        del rets["findpass_random"]
        del rets["passwd"]
    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "token unpack fail")
        logger.exception(e)
        return jsonify(operation_res_build("token unpack fail", False))

    return jsonify(operation_res_build("token unpack ok", True, data=rets))

#
# @users_bp.route("/", methods=["GET"])
# @role_auth_require(grant_all=True)
# def users_request(role, identity):
#     """
#     user信息获取
#     """
#     try:
#         if role == "system":
#             uurs = Uurs.query.offset(request.args.get("offset")).limit(request.args.get("limit")).all()
#             total = db.session.query(func.count(Uurs.uur_id)).scalar()
#         else:
#             uurs = Uurs.query.filter(Users.u_id == Uurs.u_id, Uurs.unit_id_copy == identity["unit_id"])\
#                 .offset(request.args.get("offset")).limit(request.args.get("limit")).all()
#
#             total = db.session.query(func.count(Uurs.uur_id))\
#                 .filter(Users.u_id == Uurs.u_id, Uurs.unit_id_copy == identity["unit_id"]).scalar()
#
#         users_list = []
#
#         for _ in uurs:
#             user_ = users_schema_single.dump(_.u)
#             ur_ = units_roles_schema_single.dump(_.ur)
#
#             del user_["passwd"]
#             del user_["findpass_random"]
#
#             users_list.append([user_, ur_])
#
#     except Exception as e:
#         logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "load users failed")
#         logger.exception(e)
#         return jsonify(operation_res_build("load users failed", False))
#
#     return jsonify(operation_res_build("load users ok", True, data={"user": users_list, "total": total}))


@users_bp.route("/unit_user/<int:unit_id>", methods=["GET"])
@role_auth_require(grant_all=True)
def users_request_by_unit(role, identity, unit_id):

    '''
    根据单位下的所有已激活的用户
    :param role:
    :param identity:
    :param unit_id:
    :return:
    '''

    ret = []

    try:
        unit = Units.query.filter(Units.unit_id == unit_id).first()
        if unit is None:
            return jsonify(operation_res_build(f"unit id { unit_id } does not exist", False))

        uurs = Uurs.query.filter(
            Uurs.uur_state == "1", unit_id == Uurs.unit_id_copy).offset(request.args.get("offset")).limit(request.args.get("limit")).all()

        total = db.session.query(func.count(Uurs.uur_id)).filter(Uurs.unit_id_copy == unit_id).scalar()

        for _ in uurs:
            uurs_ = uurs_schema_single.dump(_)
            user_ = users_schema_single.dump(_.u)
            ur_ = units_roles_schema_single.dump(_.ur)

            tmp = {
                "uur_id": uurs_["uur_id"],
                "uur_state": uurs_["uur_state"],
                "uur_memo": uurs_["uur_memo"],
            }

            tmp.update(user_)
            tmp.update(ur_)

            del tmp["passwd"]
            del tmp["findpass_duetime"]
            del tmp["findpass_random"]

            ret.append(tmp)

    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "load user failed")
        logger.exception(e)
        return jsonify(operation_res_build("load user failed", False))

    return jsonify(operation_res_build("load users ok", True, data={"users": ret, "total": total}))


@users_bp.route("/tel/<int:mobile>", methods=["GET"])
@role_auth_require(auth_roles=["system"])
def user_request_by_mobile(role, identity, mobile):
    """
    根据mobile获取用户信息
    :param role:
    :param identity:
    :param mobile: user-mobile
    :return:
    """
    try:
        user = Users.query.filter(Users.mobile == mobile).first()

        if user is None:
            return jsonify(operation_res_build(f"手机号 { mobile } 用户不存在", False))

        user_ = users_schema_single.dump(user)
        uurs = Uurs.query.filter(Uurs.u_id == user_["u_id"]).all()

        del user_["passwd"]
        del user_["findpass_duetime"]
        del user_["findpass_random"]

        ret = []

        for _ in uurs:
            uurs_ = uurs_schema_single.dump(_)
            ur_ = units_roles_schema_single.dump(_.ur)

            tmp = {
                "uur_id": uurs_["uur_id"],
                "uur_state": uurs_["uur_state"],
                "uur_memo": uurs_["uur_memo"],
            }

            tmp.update(user_)
            tmp.update(ur_)
            ret.append(tmp)
    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "load user failed")
        logger.exception(e)
        return jsonify(operation_res_build("load user failed", False))

    return jsonify(operation_res_build("load user ok", True, data={"users": ret}))


@users_bp.route("/psw_reset_email", methods=["PATCH"])
def user_psw_reset_by_user():
    """
    user密码重置，由用户，发送重置邮件
    """
    data = request.get_json()
    mobile = data["mobile"]
    captcha = data["captcha"]

    if session.get("captcha") != captcha:
        return jsonify(operation_res_build("captcha error", False))

    try:
        pre_sql = Users.query.filter(Users.mobile == mobile)
        user = pre_sql.first()

        if user is None:
            return jsonify(operation_res_build("the user does not exist", False))

        user_ = users_schema_single.dump(user)

        if user_["user_mail"] is None:
            return jsonify(operation_res_build("the user has no email info", False))
        else:
            sid = random_chars_gen(len_=32, ignore_capital=False)
            pre_sql.update({"findpass_random": sid,
                            "findpass_duetime": get_time_offset(offset_time_h=3)})

            if not send_mail(user_["user_mail"], sid):
                raise Exception

        db.session.commit()
    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "the user reset psw fail")
        logger.exception(e)
        return jsonify(operation_res_build("the user reset psw fail", False)), False

    return jsonify(operation_res_build("the user reset psw ok", True)), True


@users_bp.route("/psw_renew_sid_check", methods=["GET"])
def user_psw_renew_sid_check():
    """
    重置页面的sid检测
    """
    sid = request.args.get("sid")

    user = Users.query.filter(Users.findpass_random == sid).first()

    if user is None:
        return jsonify(operation_res_build("invalid sid", False))

    user_ = users_schema_single.dump(user)
    offset = get_time_gap(user_["findpass_duetime"], get_current_time())

    if offset.find("day") != -1:
        return jsonify(operation_res_build("expired sid", False))
    else:
        if int(offset[:offset.find(':')]) >= 3:
            return jsonify(operation_res_build("expired sid", False))

    return jsonify(operation_res_build("valid sid", True, data=user_["mobile"]))


@users_bp.route("/psw_renew", methods=["PATCH"])
def user_psw_renew():
    """
    user更新新密码
    """
    data = request.get_json()

    sid = data.get("sid")
    new_psw = data.get("newPsw")

    try:
        pre_sql = Users.query.filter(Users.findpass_random == sid)
        user = pre_sql.first()

        if user is None:
            return jsonify(operation_res_build("invalid sid", False)), False

        pre_sql.update({"passwd": usr_psw_generator(new_psw),
                        "findpass_duetime": current_app.config["USED_SID_DEFAULT_TIME"],
                        "findpass_random": '', "failtimes": 0})

        db.session.commit()
    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "a error happened in resetting psw")
        logger.exception(e)
        return jsonify(operation_res_build("a error happened in resetting psw", False)), False

    return jsonify(operation_res_build("resetting psw ok", True)), True


@users_bp.route("/psw_renew_login", methods=["PATCH"])
@role_auth_require(grant_all=True)
@log_info_record(LOG_ACTIONS["MOD"])
def user_psw_renew_login(role, identity):
    """
    user更新新密码，在个人信息修改
    """

    data = request.get_json()
    new_psw = data.get("pass")
    old_psw = data.get("oldpass")

    try:
        user = Users.query.filter(Users.u_id == identity["u_id"], Users.passwd == usr_psw_generator(old_psw)).first()

        if user is None:
            return jsonify(operation_res_build("旧密码不正确", False)), False

        Users.query.filter(Users.u_id == identity["u_id"]).update({
            "passwd": usr_psw_generator(new_psw),
            "failtimes": 0
        })

        db.session.commit()
    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "a error happened in resetting psw")
        logger.exception(e)
        return jsonify(operation_res_build("a error happened in resetting psw", False)), False

    return jsonify(operation_res_build("resetting psw ok", True)), True


@users_bp.route("/login", methods=["POST"])
def user_login():
    """
    user登录
    """
    data = request.get_json()

    mobile = data.get("mobile")
    passwd = data.get("passwd")
    captcha = data.get("captcha")

    try:
        # user = Users.query.filter(Users.mobile == mobile, Users.passwd == usr_psw_generator(passwd)).first()
        pre_sql = Users.query.filter(Users.mobile == mobile)
        user = pre_sql.first()

        if user is None:
            return jsonify(operation_res_build(f"user does not exist", False))

        # 是否达到尝试上限
        user_ = users_schema_single.dump(user)

        if user_["failtimes"] >= current_app.config["LOGIN_FAIL_TRIES_LIMIT"]:
            # 需要验证码验证
            if captcha is None:
                return jsonify(operation_res_build("captcha error", False))
            elif session.get("captcha").lower() != captcha.lower():
                return jsonify(operation_res_build("captcha error", False))

        if user_["passwd"] == usr_psw_generator(passwd):
            if not user_["user_state"]:
                return jsonify(operation_res_build("user account is inactive", False))
        else:
            pre_sql.update({"failtimes": user_["failtimes"] + 1})
            db.session.commit()

            return jsonify(operation_res_build("login fail", False))

        pre_sql.update({"failtimes": 0})
        db.session.commit()

        uurs = user.uurs
    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "a error happened in login")
        logger.exception(e)
        return jsonify(operation_res_build("a error happened in login", False))

    del user_["passwd"]

    uurs_ = uurs_schema.dump(uurs)
    uurs__ = [{"uur_id": uur["uur_id"], "ur_id": uur["ur_id"], "u_id": uur["u_id"]}
              for uur in uurs_ if uur["uur_state"]]

    for index, _ in enumerate(uurs):
        tmp = _.ur

        uurs_[index]["role_name"] = ROLE_ID_ROLE_NAME_REFLECTION[tmp.role_id]
        uurs_[index]["role_memo"] = ROLE_ID_ROLE_MEMO_REFLECTION[tmp.role_id]
        uurs_[index]["unit_name"] = tmp.unit_name_copy

    uurs_ = [uur for uur in uurs_ if uur["uur_state"] == 1]

    return jsonify(operation_res_build("login ok", True, data={"user": user_, "uurs": uurs_,
                                                               "token": identity_choose_token_generate(uurs__,
                                                                                                       user_["name"])}))


@users_bp.route("/role_choose", methods=["GET"])
@first_login_require
def user_role_choose(uur_id, ur_id, u_id, name):
    """
    user的uur登录选择
    """
    if uur_id == -1:
        return jsonify(operation_res_build("something wrong in choosing login role,"
                                           " it probably choose a uur_id that is not existed or inactive", False))
    try:
        ur = units_roles_schema_single.dump(UnitsRoles.query.filter(UnitsRoles.ur_id == ur_id).first())
    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), f"can not find a role in ur_id {ur_id}")
        logger.exception(e)
        return jsonify(operation_res_build(f"can not find a role in ur_id {ur_id}", False))

    if not ur["ur_state"]:
        return jsonify(operation_res_build(f"this ur_id {ur_id} is inactive", False))

    access_token = identity_confirm_token_generate(uur_id=uur_id, role_id=ur["role_id"], ur_id=ur_id, u_id=u_id,
                                                   name=name, unit_id=ur["unit_id"])

    refresh_token = identity_access_token_refresh(uur_id=uur_id, role_id=ur["role_id"], ur_id=ur_id, u_id=u_id,
                                                  name=name, unit_id=ur["unit_id"])

    return jsonify(operation_res_build("role choose ok", True,
                                       data={"access_token": access_token, "refresh_token": refresh_token}))


@users_bp.route("/psw_reset_uur_id/<int:uur_id>", methods=["PATCH"])
@role_auth_require(auth_roles=["system", "unit_manager"])
@log_info_record(LOG_ACTIONS["MOD"])
def user_psw_reset_by_manager_uur(role, identity, uur_id):
    '''
     user密码重置，由管理员重置为手机号
    :param role:
    :param identity:
    :param uur_id:
    :return:
    '''

    try:
        pre_sql_uur = Uurs.query.filter(Uurs.uur_id == uur_id, Uurs.uur_state == 1)
        uur = pre_sql_uur.first()

        if uur is None:
            return jsonify(operation_res_build("the user does not exist or is inactive", False)), False

        user_ = users_schema_single.dump(uur.u)

        pre_sql_user = Users.query.filter(Users.u_id == user_["u_id"])
        pre_sql_user.update({
            "passwd": usr_psw_generator(user_["mobile"]),
            "failtimes": 0
        })

        db.session.commit()
    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "update psw fail")
        logger.exception(e)
        return jsonify(operation_res_build("update psw fail", False)), False

    return jsonify(operation_res_build("update psw ok", True)), True


@users_bp.route("/email_update", methods=["PATCH"])
@role_auth_require(grant_all=True)
def user_email_reset(role, identity):
    user_mail = request.get_json().get("user_mail")

    if user_mail is None:
        return jsonify(operation_res_build("request params error", False))

    try:
        pre_sql = Users.query.filter(Users.u_id == identity["u_id"])
        user = pre_sql.first()

        if user is None:
            return jsonify(operation_res_build("the user does not exist or is inactive", False))

        pre_sql.update({"user_mail": user_mail})

        db.session.commit()
    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "update email fail")
        logger.exception(e)
        return jsonify(operation_res_build("update email fail", False))

    return jsonify(operation_res_build("update email ok", True))