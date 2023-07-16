import datetime

from flask import Blueprint, jsonify, request, session

from models.applicationsModel import Applications
from models.maintainDataModel import db, MaintainData

from schema.modelSchema import applications_schema_single, maintain_data_schema_single

from auth.identityAuth import role_auth_require
from utils.log import log_info_record, LOG_ACTIONS
from utils.tool import operation_res_build

import logger

mt_data_bp = Blueprint("mt_data", __name__, url_prefix="/api/mt_data")


@mt_data_bp.route("/<int:app_id>", methods=["GET"])
@role_auth_require(grant_all=True)
def mt_data_request_by_app_id(role, identity, app_id):
    try:
        mt_data = MaintainData.query.filter(MaintainData.app_id == app_id).first()

        if mt_data is None:
            return jsonify(operation_res_build("the mt_data does not exist", False))

        if role != "system":
            app_ = applications_schema_single.dump(mt_data.app)
            if app_["unit_id_copy"] != identity["unit_id"]:
                raise Exception
    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "load mt_data fail")
        logger.exception(e)
        return jsonify(operation_res_build("load mt_data fail", False))

    return jsonify(operation_res_build("load mt_data ok", True, data=maintain_data_schema_single.dump(mt_data)))


@mt_data_bp.route("/<int:app_id>", methods=["POST"])
@role_auth_require(grant_all=True)
@log_info_record(LOG_ACTIONS["ADD"])
def mt_data_add(role, identity, app_id):
    data = request.get_json()

    mt_item = data.get("mt_item")
    mt_time = data.get("mt_time")
    mt_addr = data.get("mt_addr")
    mt_cost = data.get("mt_cost")
    mt_mile = data.get("mt_mile")
    photo_mt_receipt = None
    mt_memo = data.get("mt_memo")

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

        pre_sql_mt = MaintainData.query.filter(MaintainData.app_id == app_id)
        mt_data = pre_sql_mt.first()
        add_flag = True

        if mt_data:
            pre_sql_mt.update({
                "mt_item": mt_item, "mt_addr": mt_addr, "mt_time": datetime.datetime.strptime(mt_time, "%Y-%m-%d %H:%M:%S"),
                "mt_cost": mt_cost, "mt_mile": mt_mile, "mt_memo": mt_memo
            })
            mt_data = maintain_data_schema_single.dump(mt_data)
            add_flag = False
        else:
            mt_data = MaintainData(app_id, mt_item, mt_addr, mt_time, mt_cost, mt_mile, photo_mt_receipt, mt_memo)
            db.session.add(mt_data)
            db.session.flush()

        # session["photo_upload_session"] = {"uur_id": identity["uur_id"], "app_id": app_["app_id"],
        #                                    "data_id": mt_data.mt_id if add_flag else mt_data["mt_id"],
        #                                    "type_id": type_id, "is_modified_submit": not add_flag}

        db.session.commit()
    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "a error happened in deletion")
        logger.exception(e)
        return jsonify(operation_res_build("a error happened in deletion", False)), False

    return jsonify(operation_res_build("addition ok", True, data=mt_data.mt_id if add_flag else mt_data["mt_id"])), True


@mt_data_bp.route("/<int:app_id>", methods=["GET"])
@role_auth_require(grant_all=True)
def mt_data_delete(role, identity, app_id):
    try:
        mt_data = MaintainData.query.filter(MaintainData.app_id == app_id).first()

        if mt_data is None:
            return jsonify(operation_res_build("the mt_data does not exist", False))

        if role != "system":
            app_ = applications_schema_single.dump(mt_data.app)
            if app_["unit_id_copy"] != identity["unit_id"]:
                raise Exception

        db.session.delete(mt_data)
        db.session.commit()
    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "a error happened in deletion")
        logger.exception(e)
        return jsonify(operation_res_build("a error happened in deletion", False))

    return jsonify(operation_res_build("deletion ok", True))


@mt_data_bp.route("/<int:app_id>", methods=["PUT"])
@role_auth_require(grant_all=True)
@log_info_record(LOG_ACTIONS["MOD"])
def mt_data_update(role, identity, app_id):
    data = request.get_json()

    mt_id = data.get("mt_id")
    mt_item = data.get("mt_item")
    mt_addr = data.get("mt_addr")
    mt_time = data.get("mt_time")
    mt_cost = data.get("mt_cost")
    mt_mile = data.get("mt_mile")
    photo_mt_receipt = data.get("photo_mt_receipt")
    mt_memo = data.get("mt_memo")

    try:
        mt_data = MaintainData.query.filter(MaintainData.app_id == app_id).first()

        if mt_data is None:
            return jsonify(operation_res_build("the mt_data does not exist", False)), False

        if role != "system":
            app_ = applications_schema_single.dump(mt_data.app)

            if app_["unit_id_copy"] != identity["unit_id"]:
                raise Exception

        MaintainData.query.filter(MaintainData.mt_id == mt_id).\
            update({"mt_item": mt_item, "mt_addr": mt_addr, "mt_time": mt_time, "mt_cost": mt_cost,
                    "mt_mile": mt_mile, "photo_mt_receipt": photo_mt_receipt, "mt_memo": mt_memo})

        db.session.commit()
    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "a error happened in update")
        logger.exception(e)
        return jsonify(operation_res_build("a error happened in update", False)), False

    return jsonify(operation_res_build("update ok", True)), True
