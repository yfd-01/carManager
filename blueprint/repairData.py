import datetime

from flask import Blueprint, jsonify, request, session

from models.applicationsModel import Applications
from models.repairDataModel import db, RepairData

from schema.modelSchema import applications_schema_single, repair_data_schema, repair_data_schema_single
from utils.log import log_info_record, LOG_ACTIONS

from utils.tool import operation_res_build, get_current_time
from auth.identityAuth import role_auth_require
import logger

rp_data_bp = Blueprint("rp_data", __name__, url_prefix="/api/rp_data")


@rp_data_bp.route("/", methods=["GET"])
@role_auth_require(grant_all=True)
def rp_data_request(role, unit):
    try:
        rp_data = RepairData.query.all()
    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "load rp_data failed")
        logger.exception(e)
        return jsonify(operation_res_build("load rp_data failed", False))

    return jsonify(operation_res_build("load rp_data ok", True, rp_data=repair_data_schema.dump(rp_data)))


@rp_data_bp.route("/<int:rp_id>", methods=["GET"])
@role_auth_require(grant_all=True)
def rp_data_request_by_id(unit, rp_id):
    try:
        rp_data = RepairData.query.filter(RepairData.rp_id == rp_id).first()

        if rp_data is None:
            return jsonify(operation_res_build("load rp_data is not exist", False))
    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "load rp_data failed")
        logger.exception(e)
        return jsonify(operation_res_build("load rp_data failed", False))

    return jsonify(operation_res_build("load rp_data ok", True, rp_data=repair_data_schema_single.dump(rp_data)))


@rp_data_bp.route("/<int:app_id>", methods=["POST"])
@role_auth_require(grant_all=True)
@log_info_record(LOG_ACTIONS["MOD"])
def rp_data_add(role, identity, app_id):
    data = request.get_json()

    rp_item = data.get("rp_item")
    rp_cost = data.get("rp_cost")
    rp_time = data.get("rp_time")
    rp_addr = data.get("rp_addr")
    rp_mile = data.get("rp_mile")
    photo_rp_receipt = None
    rp_memo = data.get("rp_memo")

    type_id = data.get("type_id")
    # app_memo = data.get("app_memo")

    try:
        pre_sql = Applications.query.filter(Applications.app_id == app_id, Applications.unit_id_copy == identity["unit_id"])
        app = pre_sql.first()

        if app is None:
            return jsonify(operation_res_build(f"app_id {app_id} does not exist", False)), False

        app_ = applications_schema_single.dump(app)

        if app_["flowstate_title_copy"] != "FULFILL_INFO" and app_["flowstate_title_copy"] != "INFO_UPLOAD":
            return jsonify(operation_res_build("当前申请还不能进行此操作", False)), False

        pre_sql_rp = RepairData.query.filter(RepairData.app_id == app_id)
        rp_data = pre_sql_rp.first()
        add_flag = True

        if rp_data:
            pre_sql_rp.update({
                "rp_item": rp_item, "rp_cost": rp_cost, "rp_time": datetime.datetime.strptime(rp_time, "%Y-%m-%d %H:%M:%S"),
                "rp_addr": rp_addr, "rp_mile": rp_mile, "rp_memo": rp_memo
            })
            rp_data = repair_data_schema_single.dump(rp_data)
            add_flag = False
        else:
            rp_data = RepairData(app_id, rp_item, rp_cost, rp_time, rp_addr, rp_mile, photo_rp_receipt, rp_memo)
            db.session.add(rp_data)
            db.session.flush()

        # session["photo_upload_session"] = {"uur_id": identity["uur_id"], "app_id": app_["app_id"],
        #                                    "data_id": rp_data.rp_id if add_flag else rp_data["rp_id"],
        #                                    "type_id": type_id, "is_modified_submit": not add_flag}

        # pre_sql.update({"app_memo": app_memo})

        db.session.commit()
    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "a error happened in deletion")
        logger.exception(e)
        return jsonify(operation_res_build("a error happened in deletion", False)), False

    return jsonify(operation_res_build("addition ok", True, data=rp_data.rp_id if add_flag else rp_data["rp_id"])), True
