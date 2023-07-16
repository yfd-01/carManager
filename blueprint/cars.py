from flask import Blueprint, jsonify, request
from sqlalchemy import func

from auth.msgDef import FIELD_CODE
from models.carsModel import db, Cars
from models.unitsModel import Units
from schema.modelSchema import cars_schema, cars_schema_single, units_schema, units_schema_single

from utils.log import log_info_record, LOG_ACTIONS
from utils.tool import operation_res_build
from auth.identityAuth import role_auth_require, field_check_unit

import logger
cars_bp = Blueprint("cars", __name__, url_prefix="/api/cars")


@cars_bp.route("/unit/<int:unit_id>", methods=["GET"])
@role_auth_require(grant_all=True)
def cars_request_by_unit(role, identity, unit_id):
    """
    查询公司下的所有车辆
    :param role:
    :param identity:
    :param unit_id:
    :return:
    """
    try:

        if role != "system":
            # 水平检测 判断传过来的unit_id是否为自己公司及下属公司的
            if (rc := field_check_unit(role, unit_id, identity["unit_id"])) != FIELD_CODE["PASS"]:
                return jsonify(operation_res_build("filed check fail", False, errCode=rc))

        unit = Units.query.filter(Units.unit_id == unit_id).first()
        if unit is None:
            return jsonify(operation_res_build("the units is not exist", False))

        # unit_ = units_schema_single.dump(unit)
        # units_ids = [unit_id] + secondaryUnit(unit_)   # 自身 + 二级


        cars = Cars.query.filter(Cars.unit_id == unit_id, Cars.car_state != -1)\
            .offset(request.args.get("offset")).limit(request.args.get("limit")).all()
        total = db.session.query(func.count(Cars.car_id)).filter(Cars.unit_id == unit_id, Cars.car_state != -1).scalar()

    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "load cars failed")
        logger.exception(e)
        return jsonify(operation_res_build("load car failed", False))

    return jsonify(operation_res_build("load car ok", True, data={"cars": cars_schema.dump(cars), "total": total}))


@cars_bp.route("/<int:car_id>", methods=["GET"])
@role_auth_require(grant_all=True)
def car_request_by_id(role, identity, car_id):
    """
    car信息获取，根据car_id
    """
    try:
        car = Cars.query.filter(Cars.car_id == car_id, Cars.car_state != -1).first()
        if car is None:
            return jsonify(operation_res_build("load car is not exist", False))
        car_data = cars_schema_single.dump(car)

        if (rc := field_check_unit(role, car_data["unit_id"], identity["unit_id"])) != FIELD_CODE["PASS"]:
            return jsonify(operation_res_build("filed check fail", False, errCode=rc))

    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "load car failed")
        logger.exception(e)
        return jsonify(operation_res_build("load car failed", False))

    return jsonify(operation_res_build("load car ok", True, data=car_data))


@cars_bp.route("/", methods=["POST"])
@role_auth_require(grant_all=True)
@log_info_record(LOG_ACTIONS["ADD"])
def car_add(role, identity):
    """
    car添加
    """
    data = request.get_json()

    palte_number = data.get("palte_number")
    car_type = data.get("car_type")
    car_brand = data.get("car_brand")
    gas_type = data.get("gas_type")
    tank_capacity = data.get("tank_capacity")
    car_state = data.get("car_state") if data.get("car_state") is not None else 1
    card_number = data.get("card_number")
    capital_balance = 0
    unit_id = data.get("unit_id")
    car_memo = data.get("car_memo")

    try:
        car = Cars.query.filter(Cars.palte_number == palte_number, Cars.car_state != -1).first()

        if car:
            unit_id_ = cars_schema_single.dump(car)["unit_id"]
            unit_ = units_schema_single.dump(Units.query.filter(Units.unit_id == unit_id_).first())

            return jsonify(operation_res_build(f"{palte_number} 车辆已被 {unit_['unit_name']} 添加", False)), False

        db.session.add(Cars(unit_id, palte_number, car_type, car_brand, gas_type, tank_capacity, car_state, card_number,
                            capital_balance, car_memo))
        db.session.commit()
    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "a error happened in addition")
        logger.exception(e)
        return jsonify(operation_res_build("a error happened in addition", False)), False

    return jsonify(operation_res_build("add ok", True)), True


@cars_bp.route("/<int:car_id>", methods=["DELETE"])
@role_auth_require(auth_roles=["system", "unit_manager"])
@log_info_record(LOG_ACTIONS["DEL"])
def car_delete(role, identity, car_id):
    """
    car激活或禁用
    """
    try:
        pre_sql = Cars.query.filter(Cars.car_id == car_id)
        car = pre_sql.first()

        if not car:
            jsonify(operation_res_build("car does not exist", False)), False

        car_ = cars_schema_single.dump(car)

        if role != "system":
            if (rc := field_check_unit(role, car_["unit_id"], identity["unit_id"])) != FIELD_CODE["PASS"]:
                return jsonify(operation_res_build("filed check fail", False, errCode=rc))

        pre_sql.update({"car_state": '-1'})
        db.session.commit()
    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "a error happened in deletion")
        logger.exception(e)
        return jsonify(operation_res_build("a error happened in deletion", False)), False

    return jsonify(operation_res_build("deletion ok", True)), True


@cars_bp.route("/<int:car_id>", methods=["PUT"])
@role_auth_require(grant_all=True)
@log_info_record(LOG_ACTIONS["MOD"])
def car_update(role, identity, car_id):
    """
    car更新
    """
    data = request.get_json()

    unit_id = data.get("unit_id")
    palte_number = data.get("palte_number")
    car_type = data.get("car_type")
    car_brand = data.get("car_brand")
    gas_type = data.get("gas_type")
    tank_capacity = data.get("tank_capacity")
    car_state = data.get("car_state") if data.get("car_state") is not None else 1
    card_number = data.get("card_number")
    # capital_balance = data.get("capital_balance")
    car_memo = data.get("car_memo")

    try:
        pre_sql = Cars.query.filter(Cars.car_id == car_id)
        if not len(pre_sql.all()):
            return jsonify(operation_res_build("车辆信息不存在！", False)), False

        pre_sql.update({"unit_id": unit_id, "palte_number": palte_number,
                        "car_type": car_type, "car_brand": car_brand, "gas_type": gas_type,
                        "tank_capacity": tank_capacity, "car_state": car_state, "card_number": card_number,
                        "car_memo": car_memo})
        db.session.commit()
    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "a error happened in update")
        logger.exception(e)
        return jsonify(operation_res_build("a error happened in update", False)), False

    return jsonify(operation_res_build("update ok", True)), True


@cars_bp.route("/plate/<string:query>", methods=["GET"])
@role_auth_require(auth_roles=["system"])
def car_input_search(role, identity, query):
    try:
        if query is None:
            cars = Cars.query.filter().all()
        else:
            cars = Cars.query\
                .filter(True if query is None else Cars.palte_number.ilike(f"%{query}%")).all()

    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "load car failed")
        logger.exception(e)
        return jsonify(operation_res_build("load car ok", data={"cars": cars_schema.dump(cars)}))

    return jsonify(operation_res_build("load car ok", True, data={"cars": cars_schema.dump(cars)}))
