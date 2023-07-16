import datetime

from flask_jwt_extended import create_access_token, create_refresh_token, \
    get_jwt_identity, get_jwt, JWTManager, verify_jwt_in_request
from flask import jsonify, current_app, request
from functools import wraps

from utils.tool import operation_res_build, logging_content_assemble
from auth.msgDef import CLAIM, CODE, ROLE_NAME_ROLE_ID_REFLECTION, ROLE_ID_ROLE_NAME_REFLECTION,\
    TYPE_ID_TYPE_NAME_REFLECTION, FIELD_CODE
from exceptions import AuthRolesIsNotExisted, AuthRolesTypeError, AuthRolesParamError
import logger

from models.uursModel import Uurs
from models.unitsModel import Units
from models.maintainDataModel import MaintainData
from models.rechargeDataModel import RechargeData
from models.refuelDataModel import RefuelData
from models.repairDataModel import RepairData

from schema.modelSchema import units_schema_single, applications_schema_single

jwt = JWTManager()


# ----异常行为捕捉
# 非法令牌
@jwt.invalid_token_loader
def __signature_verification_failed(e):
    logger.warning(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "令牌非法")
    return jsonify(operation_res_build(CLAIM["INVALID"], False, errCode=CODE["INVALID"]))


# 缺少令牌
@jwt.unauthorized_loader
def __missing_auth_header(e):
    logger.warning(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "令牌缺失")
    return jsonify(operation_res_build(CLAIM["MISS"], False, errCode=CODE["MISS"]))


# 过期令牌
@jwt.expired_token_loader
def expired_token_callback(h, d):
    logger.warning(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "令牌过期")
    return jsonify(operation_res_build(CLAIM["EXPIRED"], False, errCode=CODE["EXPIRED"]))


# 角色选择前置装饰器
def first_login_require(view_func):
    """
    用于角色选择的令牌验证，防止csrf
    """

    @wraps(view_func)
    def wrapper():
        verify_jwt_in_request()
        logger.info(request.environ.get('HTTP_X_REAL_IP', request.remote_addr),
                    logging_content_assemble(request.url, request.get_json(silent=True)))

        jwt_ = get_jwt()
        uur_id = int(request.args["uur_id"])
        ur_id = -1
        u_id = -1

        valid_flag = False

        for uur in jwt_["sub"]:
            if int(uur["uur_id"]) == int(uur_id):
                ur_id = uur["ur_id"]
                u_id = uur["u_id"]
                valid_flag = True

                break

        if not jwt_["to_login_identity_token"] or not valid_flag:
            uur_id = -1

        return view_func(uur_id, ur_id, u_id, jwt_["name"])

    return wrapper


# 限制性访问装饰器
def role_auth_require(**kwargs):
    """
    用于限制接口访问角色
    :param auth_roles: 可访问角色 - `List`
    :param grant_all:  授权全部 - `Bool` - optional
    """

    grant_all_flag = False

    # 是否有grant_all参数
    if "grant_all" in kwargs:
        grant_all_flag = kwargs["grant_all"]

    # 没有grant_all参数并且没有指定访问权限角色
    if not grant_all_flag and "auth_roles" not in kwargs:
        raise AuthRolesParamError(**kwargs)

    if "auth_roles" in kwargs:
        auth_roles = kwargs["auth_roles"]

        if not isinstance(auth_roles, list):    # 非列表传入
            raise AuthRolesTypeError(auth_roles)

        # 检测访问权限角色是否存在
        if not all([role in ROLE_NAME_ROLE_ID_REFLECTION for role in auth_roles]) or not len(auth_roles):
            raise AuthRolesIsNotExisted(auth_roles)

        # 当前接口的授权角色id合集
        auth_roles_ids = [ROLE_NAME_ROLE_ID_REFLECTION[role] for role in auth_roles]

    def wrapper(view_func):
        @wraps(view_func)
        def decorator(**kwargs_):
            verify_jwt_in_request()
            identity = get_jwt_identity()

            logger.info(request.environ.get('HTTP_X_REAL_IP', request.remote_addr),
                        logging_content_assemble(request.url, request.get_json(silent=True)))
            # 是否使用了以前的令牌（令牌未过期但角色已无效）
            uur = Uurs.query.filter(identity["uur_id"] == Uurs.uur_id, Uurs.uur_state == 1).first()

            if uur is None:
                return jsonify(operation_res_build(CLAIM["INACTIVE"], False, errCode=CODE["INACTIVE"]))

            if isinstance(identity, list):
                return jsonify(operation_res_build(CLAIM["NO_RIGHT"], False, errCode=CODE["NO_RIGHT"]))

            if grant_all_flag:
                # if not field_right_check(identity["unit_id"]):
                #     return jsonify(operation_res_build(CLAIM["NO_RIGHT"], False, errCode=CODE["NO_RIGHT"]))

                return view_func(ROLE_ID_ROLE_NAME_REFLECTION[identity["role_id"]], identity, **kwargs_)
            else:
                # 判断当前用户角色是否在授权角色集中
                if identity["role_id"] in auth_roles_ids:
                    # if not field_right_check(identity["unit_id"]):
                    #     return jsonify(operation_res_build(CLAIM["NO_RIGHT"], False, errCode=CODE["NO_RIGHT"]))

                    return view_func(ROLE_ID_ROLE_NAME_REFLECTION[identity["role_id"]], identity, **kwargs_)
                else:
                    return jsonify(operation_res_build(CLAIM["NO_RIGHT"], False, errCode=CODE["NO_RIGHT"]))

        return decorator

    return wrapper


# 过期刷新前置装饰器
def expired_token_require(view_func):
    @wraps(view_func)
    def wrapper():
        # 要求令牌必须为刷新令牌，普通令牌无效
        verify_jwt_in_request(refresh=True)
        logger.info(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "令牌刷新")

        jwt_ = get_jwt()
        uur_id = int(request.args["uur_id"])
        identity = jwt_["sub"]

        to_refresh = False

        if jwt_["to_refresh_identity_token"] and identity["uur_id"] == uur_id:
            to_refresh = True

        return view_func(to_refresh, identity)

    return wrapper


# 图片上传凭证检测装饰器
def app_upload_params_check(view_func):
    @wraps(view_func)
    def wrapper(role, identity):
        is_receipt = request.args.get("is_receipt")
        # session_ = session.get("photo_upload_session")
        #
        # if session_ is None:
        #     return jsonify(operation_res_build("session credential is required", False))

        # app_id = session_["app_id"]
        # data_id = session_["data_id"]
        # type_id = session_["type_id"]

        app_id = request.args.get("app_id")
        data_id =request.args.get("data_id")
        type_id = request.args.get("type_id")


        if app_id is None or data_id is None or is_receipt is None or type_id is None:
            return jsonify(operation_res_build("error request params", False))

        # 检查 type_id
        try:
            type_id = int(type_id)
            type_name = TYPE_ID_TYPE_NAME_REFLECTION[type_id]
        except ValueError or KeyError:
            return jsonify(operation_res_build("error request params", False))

        # 检查 app_id与mt_id是否对应
        if type_name == "maintaindata":
            data = MaintainData.query.filter(MaintainData.mt_id == data_id).first()
        elif type_name == "rechargedata":
            data = RechargeData.query.filter(RechargeData.rc_id == data_id).first()
        elif type_name == "refueldata":
            data = RefuelData.query.filter(RefuelData.ref_id == data_id).first()
        elif type_name == "repairdata":
            data = RepairData.query.filter(RepairData.rp_id == data_id).first()
        else:
            return jsonify(operation_res_build("unknown error", False))

        if data is None:
            return jsonify(operation_res_build(f"you need to take a previous step to be here", False))

        app_ = applications_schema_single.dump(data.app)

        if app_["unit_id_copy"] != identity["unit_id"]:
            # 这个app不是登录用户公司的
            return jsonify(
                operation_res_build("you cant access the resource that is not belong to your unit", False))
        elif app_["flowstate_title_copy"] != "FULFILL_INFO" and app_["flowstate_title_copy"] != "INFO_UPLOAD":
            # 这个app的状态不是待完善资料
            return jsonify(operation_res_build("app error status", False))
        elif app_["app_id"] != int(app_id):
            # app_id与mt_id无法对应
            return jsonify(operation_res_build("error combination of app_id and mt_id", False))

        return view_func(role, identity, app_id, data_id, request.files.getlist("file")[0], is_receipt)

    return wrapper


# ----令牌生成
# 身份令牌生成 - 资源访问
def identity_confirm_token_generate(*, u_id, name, uur_id, ur_id, role_id, unit_id):
    return create_access_token(identity={"u_id": u_id, "name": name, "uur_id": uur_id, "ur_id": ur_id,
                                         "role_id": role_id, "unit_id": unit_id},
                               expires_delta=datetime.timedelta(seconds=current_app.config["ACCESS_TOKEN_EXIST"]))


# 登录令牌生成 - 验证登录
def identity_choose_token_generate(uurs, name):
    return create_access_token(identity=uurs, additional_claims={"to_login_identity_token": True, "name": name},
                               expires_delta=datetime.timedelta(seconds=current_app.config["LOGIN_CHOOSE_TOKEN_EXIST"]))


# 刷新令牌生成 - 刷新过期资源访问token
def identity_access_token_refresh(*, u_id, name, uur_id, ur_id, role_id, unit_id):
    return create_refresh_token(identity={"u_id": u_id, "name": name, "uur_id": uur_id, "ur_id": ur_id,
                                          "role_id": role_id, "unit_id": unit_id},
                                additional_claims={"to_refresh_identity_token": True},
                                expires_delta=datetime.timedelta(seconds=current_app.config["REFRESH_TOKEN_EXIST"]))


# ----垂直权限检测
# UNIT FIELD
def field_check_unit(role, access_unit_id, identity_unit_id):
    try:
        access_unit_id = int(access_unit_id)
        identity_unit_id = int(identity_unit_id)
    except ValueError:
        return FIELD_CODE["INVALID"]

    if role == "system":
        return FIELD_CODE["PASS"]

    try:
        unit = Units.query.filter(Units.unit_id == access_unit_id).first()

        while True:
            if unit is None:
                return FIELD_CODE["NO_RIGHT"]
            else:
                unit_ = units_schema_single.dump(unit)

                if unit_["unit_id"] == identity_unit_id:
                    return FIELD_CODE["PASS"]
                else:
                    unit = Units.query.filter(Units.unit_id == unit_["parent_unit_id"]).first()
    except Exception:
        return FIELD_CODE["SERVER_ERR"]
