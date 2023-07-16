from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity

from auth.identityAuth import role_auth_require, field_check_unit
from auth.msgDef import ROLE_ID_ROLE_MEMO_REFLECTION, ROLE_NAME_ROLE_ID_REFLECTION, FIELD_CODE

from fsm.flow import Flow
from models.flowsModel import db, Flows
from models.applicationsModel import Applications
from models.unitsModel import Units
from models.unitsRolesModel import UnitsRoles
from models.carsModel import Cars
from models.refuelDataModel import RefuelData
from models.rechargeDataModel import RechargeData
from schema.modelSchema import flows_schema_single, applications_schema_single,\
    cars_schema_single, refuel_data_schema_single, recharge_data_schema_single,\
    units_schema_single, units_roles_schema_single

from utils.tool import operation_res_build, get_current_time, get_time_gap, auth_role_exclude
from utils.log import log_info_record, LOG_ACTIONS
import logger

flows_bp = Blueprint("flows", __name__, url_prefix="/api/flows")


# @flows_bp.route("/", methods=["GET"])
# @role_auth_require(grant_all=True)
# def flows_request(role, identity):
#     try:
#         if role == "system":
#             flows = Flows.query.offset(request.args.get("offset")).limit(request.args.get("limit")).all()
#             total = db.session.query(func.count(Flows.flowstate_id)).scalar()
#         else:
#             flows = Flows.query.join(Applications).filter(Applications.unit_id_copy == identity["unit_id"])\
#                 .offset(request.args.get("offset")).limit(request.args.get("limit")).all()
#
#             total = db.session.query(func.count(Flows.flowstate_id))\
#                 .join(Applications).filter(Applications.unit_id_copy == identity["unit_id"]).scalar()
#     except Exception as e:
#         logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "load flows failed")
#         logger.exception(e)
#         return jsonify(operation_res_build("load flows failed", False))
#
#     return jsonify(operation_res_build("load flows ok", True, data={"flows": flows_schema.dump(flows), "total": total}))


@flows_bp.route("/<int:flowstate_id>", methods=["GET"])
@role_auth_require(grant_all=True)
def flow_request_by_id(role, identity, flowstate_id):
    try:
        if role == "system":
            flow = Flows.query.filter(Flows.flowstate_id == flowstate_id).first()
        else:
            flow = Flows.query.join(Applications)\
                .filter(Flows.flowstate_id == flowstate_id, Applications.unit_id_copy == identity["unit_id"]).first()

        if flow is None:
            return jsonify(operation_res_build("load flow is not exist", False))
    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "load flows failed")
        logger.exception(e)
        return jsonify(operation_res_build("load flow failed", False))

    return jsonify(operation_res_build("load flow ok", True, data=flows_schema_single.dump(flow)))


@flows_bp.route("/", methods=["POST"])
@role_auth_require(grant_all=True)
@log_info_record(LOG_ACTIONS["ADD"])
def flow_add(role, identity):
    if role == "system":
        return jsonify(operation_res_build("system cant add flow", False)), False

    data = request.get_json()

    app_id = data.get("app_id")
    event = int(data.get("event"))

    # 查询这个app是否存在
    app = Applications.query.filter(Applications.app_id == app_id).first()
    if app is None:
        return jsonify(operation_res_build(f"app_id { app_id } does not exist", False)), False

    app_ = applications_schema_single.dump(app)

    # 流程状态机初始化
    flow_fsm = Flow()

    # 添加流程权限检查
    if event != flow_fsm.EVENTS_SET["APP_DONE_BACK"]:
        if app_["ur_id"]:
            if app_["ur_id"] != identity["ur_id"]:
                return jsonify(operation_res_build(f"app_id { app_id } is out of range of operation area", False)), False
        else:
            if app_["uur_id"] != identity["uur_id"]:
                return jsonify(operation_res_build(f"you can not operate app_id { app_id } which is not belong to you", False)), False

    uur_id = identity["uur_id"]

    # 获取app最新的流程
    last_flow = Flows.query.filter(Flows.app_id == app_id).order_by(Flows.flowstate_time.desc()).first()
    _last_flow = None
    if last_flow is not None:
        _last_flow = flows_schema_single.dump(last_flow)

    cur_state = 1 if last_flow is None else flow_fsm.STATES_SET[_last_flow["flowstate_title"]]

    # 完成的申请回退检查
    if event == flow_fsm.EVENTS_SET["APP_DONE_BACK"] and role not in ["system", "unit_manager", "unit_leader"]:
        return jsonify(operation_res_build("the role you login do not have the right to back app", False)), False

    # 紧急流程添加检查
    if event == flow_fsm.EVENTS_SET["EMERGENCY_APP_FLY"] and app_["flowstate_title_copy"] != '':
        return jsonify(operation_res_build(f"app_id { app_id } is not in a certain status that arouse emergency flow", False)), False

    flow_res = flow_fsm.step(cur_state, event)
    if flow_res is None:
        return jsonify(operation_res_build(f"the combined meaning of cur_state { cur_state } and event { event } is "
                                           f"not able to be understood", False)), False
    else:
        cur_state = flow_res["new_state"]

    flowstate_title = flow_fsm.trans_state(cur_state)
    flowstate_event = flow_fsm.trans_event(event)

    flowstate_time = get_current_time()

    flowstate_spendtime = None if last_flow is None \
        else get_time_gap(get_current_time(), _last_flow["flowstate_time"])

    identity = get_jwt_identity()
    operator_role_name_copy = f'{identity["name"]}[{ROLE_ID_ROLE_MEMO_REFLECTION[identity["role_id"]]}]'
    comment = data.get("comment")

    try:
        db.session.add(Flows(app_id, uur_id, identity["unit_id"], flowstate_title, flowstate_event, flowstate_time,
                             flowstate_spendtime, operator_role_name_copy, comment))

        ur_id = None
        if flowstate_title == "OFFICER_REVIEW" or flowstate_title == "LEADER_REVIEW" or flowstate_title == "INFO_CHECK":
            unit = Units.query.filter(Units.unit_id == app_["unit_id_copy"]).first()
            if unit is None:
                return jsonify(operation_res_build(f"unit_id {app_['unit_id_copy']} does not exist", False)), False

            p_unit_id = units_schema_single.dump(unit)["parent_unit_id"]

            if flowstate_title == "LEADER_REVIEW":
                handle_role_name = "unit_leader"
            else:
                handle_role_name = "subunit_officer" if p_unit_id else "unit_officer"

            ur = UnitsRoles.query.filter(UnitsRoles.unit_id == (app_["unit_id_copy"]
                                                                if flowstate_title in ["OFFICER_REVIEW", "INFO_CHECK"] else
                                                                (p_unit_id if p_unit_id else app_["unit_id_copy"])),
                                         UnitsRoles.role_id == ROLE_NAME_ROLE_ID_REFLECTION[handle_role_name],
                                         UnitsRoles.ur_state == 1).first()
            if ur is None:
                db.session.rollback()
                return jsonify(operation_res_build(f"cant find a proper ur to handle this specific process", False)), False

            ur_id = units_roles_schema_single.dump(ur)["ur_id"]

        if flowstate_event == "LEADER_PASS":
            if app_["type_name_copy"] == "refueldata":
                __do_refuel(app_)
            elif app_["type_name_copy"] == "rechargedata":
                __do_recharge(app_)

        elif flowstate_event == "APP_DONE_BACK":
            if not __do_done_app_money(app_):
                # return jsonify(
                #     operation_res_build(f"refuelData or rechargeData in app_id {app_['app_id']} does not exist",
                #                         False)), False
                # 之前的代码会导致只有 加油申请 和 充值申请的回退生效
                pass

        # 更新app表里的flowstate_title_copy、flowstate_time_copy, app_time_end（如果流程已结束）
        Applications.query.filter(Applications.app_id == app_id).update({"flowstate_title_copy": flowstate_title,
                                                                         "flowstate_time_copy": flowstate_time,
                                                                         "app_time_end": get_current_time() if
                                                                         (flowstate_title == "WITHDRAW" or flowstate_title == "DONE") else None,
                                                                         "ur_id": ur_id})
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "a error happened in addition")
        logger.exception(e)
        return jsonify(operation_res_build("a error happened in addition", False)), False

    return jsonify(operation_res_build("addition ok", True, data=flow_res)), True


def __do_refuel(app_):
    # 加油申请完成后，需要从车辆的油卡里面减钱
    pre_sql = Cars.query.filter(Cars.car_id == app_["car_id"])
    car = pre_sql.first()
    ref = RefuelData.query.filter(RefuelData.app_id == app_["app_id"]).first()

    if car is None:
        return jsonify(operation_res_build(f"car_id {app_['car_id']} does not exist", False)), False

    if ref is None:
        return jsonify(operation_res_build(f"refuelData in app_id { app_['app_id'] } does not exist", False)), False

    car_ = cars_schema_single.dump(car)
    ref_ = refuel_data_schema_single.dump(ref)

    remaining = car_["capital_balance"] - ref_["ref_cost"]
    pre_sql.update({
        "capital_balance": remaining
    })


def __do_recharge(app_):
    pre_sql = Cars.query.filter(Cars.car_id == app_["car_id"])
    car = pre_sql.first()
    rc = RechargeData.query.filter(RechargeData.app_id == app_['app_id']).first()

    if car is None:
        return jsonify(operation_res_build(f"car_id {app_['car_id']} does not exist", False)), False

    if rc is None:
        return jsonify(operation_res_build(f"rechargeData in app_id { app_['app_id'] } does not exist", False)), False

    car_ = cars_schema_single.dump(car)
    rc_ = recharge_data_schema_single.dump(rc)

    pre_sql.update({
        "capital_balance": car_["capital_balance"] + rc_["rc_value"]
    })


def __do_done_app_money(app_):
    pre_sql = Cars.query.filter(Cars.car_id == app_["car_id"])
    car = pre_sql.first()

    if not car:
        return jsonify(operation_res_build(f"car_id {app_['car_id']} does not exist", False)), False

    ref = RefuelData.query.filter(RefuelData.app_id == app_['app_id']).order_by(RefuelData.ref_id.desc()).first()
    rc = RechargeData.query.filter(RechargeData.app_id == app_["app_id"]).order_by(RechargeData.rc_id.desc()).first()

    if not ref and not rc:
        return False

    car_ = cars_schema_single.dump(car)
    if ref:
        positive_symbol = True
        ref_ = refuel_data_schema_single.dump(ref)
    elif rc:
        positive_symbol = False
        rc_ = recharge_data_schema_single.dump(rc)

    pre_sql.update({
        "capital_balance": car_["capital_balance"] + (ref_["ref_cost"] if positive_symbol else -rc_["rc_value"])
    })

    return True


@flows_bp.route("/<int:flowstate_id>", methods=["DELETE"])
@role_auth_require(auth_roles=["system", "unit_manager"])
@log_info_record(LOG_ACTIONS["DEL"])
def flow_delete(role, identity, flowstate_id):
    try:
        if role == "system":
            db.session.delete(Flows.query.filter(Flows.flowstate_id == flowstate_id).first())
        else:
            db.session.delete(Flows.query.join(Applications)
                              .filter(Flows.flowstate_id == flowstate_id,
                                      Applications.unit_id_copy == identity["unit_id"] if role != "system" else True).first())
        db.session.commit()
    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "a error happened in deletion")
        logger.exception(e)
        return jsonify(operation_res_build("a error happened in deletion", False)), False

    return jsonify(operation_res_build("deletion ok", True)), True
