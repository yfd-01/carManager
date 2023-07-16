import datetime

from flask import Blueprint, jsonify, request, session

from models.applicationsModel import Applications
from models.refuelDataModel import db, RefuelData
from schema.modelSchema import applications_schema_single, refuel_data_schema_single

from auth.identityAuth import role_auth_require
from utils.log import log_info_record, LOG_ACTIONS
from utils.tool import operation_res_build
import logger

ref_data_bp = Blueprint("ref_data", __name__, url_prefix="/api/ref_data")


@ref_data_bp.route("/<int:app_id>", methods=["GET"])
@role_auth_require(grant_all=True)
def ref_data_request_by_app_id(role, identity, app_id):
    try:
        ref_data = RefuelData.query.filter(RefuelData.app_id == app_id).first()

        if ref_data is None:
            return jsonify(operation_res_build("the ref_data does not exist", False))

        if role != "system":
            app_ = applications_schema_single.dump(ref_data.app)
            if app_["unit_id_copy"] != identity["unit_id"]:
                raise Exception
    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "load ref_data fail")
        logger.exception(e)
        return jsonify(operation_res_build("load ref_data fail", False))

    return jsonify(operation_res_build("load ref_data ok", True, data=refuel_data_schema_single.dump(ref_data)))


@ref_data_bp.route("/<int:app_id>", methods=["POST"])
@role_auth_require(grant_all=True)
@log_info_record(LOG_ACTIONS["ADD"])
def ref_data_add(role, identity, app_id):
    data = request.get_json()

    ref_self = data.get("ref_self")
    ref_price = data.get("ref_price")
    ref_volume = data.get("ref_volume")
    ref_cost = data.get("ref_cost")
    capital_balance_copy = 0
    ref_remainder = data.get("ref_remainder")
    ref_finished_scale = data.get("ref_finished_scale")
    ref_time = data.get("ref_time")
    ref_addr = data.get("ref_addr")
    ref_gas_type = data.get("ref_gas_type")
    ref_mile = data.get("ref_mile")
    photo_ref_receipt = None
    ref_memo = data.get("ref_memo")
    type_id = data.get("type_id")
    # app_memo = data.get("app_memo")

    try:
        if float(ref_cost) < 0:
            return jsonify(operation_res_build("消费金额不能为负！", False)), False

        if float(ref_self) and not ref_mile:
            return jsonify(operation_res_build("为本车加油必填公里数！", False)), False

        pre_sql = Applications.query.filter(Applications.app_id == app_id, Applications.unit_id_copy == identity["unit_id"])
        app = pre_sql.first()

        if app is None:
            return jsonify(operation_res_build(f"app_id {app_id} does not exist", False)), False

        app_ = applications_schema_single.dump(app)

        if app_["flowstate_title_copy"] != "FULFILL_INFO" and app_["flowstate_title_copy"] != "INFO_UPLOAD":
            return jsonify(operation_res_build("当前申请还不能进行此操作", False)), False

        pre_sql_ref = RefuelData.query.filter(RefuelData.app_id == app_id)
        ref_data = pre_sql_ref.first()
        add_flag = True

        if ref_data:
            pre_sql_ref.update({
                "ref_self": ref_self, "ref_price": ref_price, "ref_volume": ref_volume, "ref_cost": ref_cost,
                "capital_balance_copy": capital_balance_copy, "ref_remainder": ref_remainder,
                "ref_finished_scale": ref_finished_scale,
                "ref_time": datetime.datetime.strptime(ref_time, "%Y-%m-%d %H:%M:%S"), "ref_addr": ref_addr,
                "ref_gas_type": ref_gas_type, "ref_mile": ref_mile, "ref_memo": ref_memo
            })
            ref_data = refuel_data_schema_single.dump(ref_data)
            add_flag = False
        else:
            ref_data = RefuelData(app_id, ref_self, ref_price, ref_volume, ref_cost, capital_balance_copy, ref_remainder, ref_finished_scale,
                                  ref_time, ref_addr, ref_gas_type, ref_mile, photo_ref_receipt, ref_memo)
            db.session.add(ref_data)
            db.session.flush()

        # session["photo_upload_session"] = {"uur_id": identity["uur_id"], "app_id": app_["app_id"],
        #                                    "data_id": ref_data.ref_id if add_flag else ref_data["ref_id"],
        #                                    "type_id": type_id, "is_modified_submit": not add_flag}

        # pre_sql.update({"app_memo": app_memo})

        db.session.commit()
    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "a error happened in addition")
        logger.exception(e)
        return jsonify(operation_res_build("a error happened in addition", False)), False

    return jsonify(operation_res_build("addition ok", True, data=ref_data.ref_id if add_flag else ref_data["ref_id"])), True


@ref_data_bp.route("/<int:app_id>", methods=["GET"])
@role_auth_require(grant_all=True)
def ref_data_delete(role, identity, app_id):
    try:
        ref_data = RefuelData.query.filter(RefuelData.app_id == app_id).first()

        if ref_data is None:
            return jsonify(operation_res_build("the ref_data does not exist", False))

        if role != "system":
            app_ = applications_schema_single.dump(ref_data.app)
            if app_["unit_id_copy"] != identity["unit_id"]:
                raise Exception

        db.session.delete(ref_data)
        db.session.commit()
    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "a error happened in deletion")
        logger.exception(e)
        return jsonify(operation_res_build("a error happened in deletion", False))

    return jsonify(operation_res_build("deletion ok", True))


@ref_data_bp.route("/<int:app_id>", methods=["PUT"])
@role_auth_require(grant_all=True)
@log_info_record(LOG_ACTIONS["MOD"])
def ref_data_update(role, identity, app_id):
    data = request.get_json()

    ref_id = data.get("ref_id")
    ref_self = data.get("ref_self")
    ref_price = data.get("ref_price")
    ref_volume = data.get("ref_volume")
    ref_cost = data.get("ref_cost")

    ref_remainder = data.get("ref_remainder")
    ref_finished_scale = data.get("ref_finished_scale")
    ref_time = data.get("ref_time")
    ref_addr = data.get("ref_addr")
    ref_gas_type = data.get("ref_gas_type")
    ref_mile = data.get("ref_mile")
    photo_ref_receipt = data.get("photo_ref_receipt")
    ref_memo = data.get("ref_memo")

    try:
        if int(ref_cost) < 0:
            return jsonify(operation_res_build("消费金额不能为负！", False)), False

        ref_data = RefuelData.query.filter(RefuelData.app_id == app_id).first()

        if ref_data is None:
            return jsonify(operation_res_build("the ref_data does not exist", False)), False

        if role != "system":
            app_ = applications_schema_single.dump(ref_data.app)

            if app_["unit_id_copy"] != identity["unit_id"]:
                raise Exception

        RefuelData.query.filter(RefuelData.ref_id == ref_id). \
            update({"app_id": app_id, "ref_self": ref_self, "ref_price": ref_price, "ref_volume": ref_volume,
                    "ref_cost": ref_cost, "ref_remainder": ref_remainder, "ref_finished_scale": ref_finished_scale,
                    "ref_time": ref_time, "ref_addr": ref_addr, "ref_gas_type": ref_gas_type, "ref_mile": ref_mile,
                    "photo_ref_receipt": photo_ref_receipt, "ref_memo": ref_memo})

        db.session.commit()
    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "a error happened in update")
        logger.exception(e)
        return jsonify(operation_res_build("a error happened in update", False)), False

    return jsonify(operation_res_build("update ok", True)), True

