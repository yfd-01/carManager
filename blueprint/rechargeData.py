import datetime
from os.path import join

from flask import Blueprint, jsonify, request, session, current_app

from models.applicationsModel import Applications
from models.rechargeDataModel import db, RechargeData
from schema.modelSchema import applications_schema_single, recharge_data_schema_single

from auth.identityAuth import role_auth_require, app_upload_params_check
from utils.log import log_info_record, LOG_ACTIONS
from utils.tool import operation_res_build, upload_preparation, file_name_picker
import logger

rc_data_bp = Blueprint("rc_data", __name__, url_prefix="/api/rc_data")


@rc_data_bp.route("/<int:app_id>", methods=["GET"])
@role_auth_require(grant_all=True)
def rc_data_request_by_app_id(role, identity, app_id):
    try:
        rc_data = RechargeData.query.filter(RechargeData.app_id == app_id).first()

        if rc_data is None:
            return jsonify(operation_res_build("the rc_data does not exist", False))

        if role != "system":
            app_ = applications_schema_single.dump(rc_data.app)
            if app_["unit_id_copy"] != identity["unit_id"]:
                raise Exception
    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "load rc_data fail")
        logger.exception(e)
        return jsonify(operation_res_build("load rc_data fail", False))

    return jsonify(operation_res_build("load rc_data ok", True, data=recharge_data_schema_single.dump(rc_data)))


@rc_data_bp.route("/<int:app_id>", methods=["POST"])
@role_auth_require(grant_all=True)
@log_info_record(LOG_ACTIONS["ADD"])
def rc_data_add(role, identity, app_id):
    data = request.get_json()

    rc_value = data.get("rc_value")
    rc_time = data.get("rc_time")
    photo_rc_receipt = None
    rc_memo = data.get("rc_memo")

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

        pre_sql_rc = RechargeData.query.filter(RechargeData.app_id == app_id)
        rc_data = pre_sql_rc.first()
        add_flag = True

        if rc_data:
            pre_sql_rc.update({
                "rc_value": rc_value, "rc_time": datetime.datetime.strptime(rc_time, "%Y-%m-%d %H:%M:%S"), "rc_memo": rc_memo
            })
            rc_data = recharge_data_schema_single.dump(rc_data)
            add_flag = False
        else:
            rc_data = RechargeData(app_id, rc_value, rc_time, photo_rc_receipt, rc_memo)
            db.session.add(rc_data)
            db.session.flush()

        # session["photo_upload_session"] = {"uur_id": identity["uur_id"], "app_id": app_["app_id"],
        #                                    "data_id": rc_data.rc_id if add_flag else rc_data["rc_id"],
        #                                    "type_id": type_id, "is_modified_submit": not add_flag}

        # pre_sql.update({"app_memo": app_memo})

        db.session.commit()
    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "a error happened in deletion")
        logger.exception(e)
        return jsonify(operation_res_build("a error happened in deletion", False)), False

    return jsonify(operation_res_build("addition ok", True, data=rc_data.rc_id if add_flag else rc_data["rc_id"])), True


@rc_data_bp.route("/<int:app_id>", methods=["GET"])
@role_auth_require(grant_all=True)
def rc_data_delete(role, identity, app_id):
    try:
        rc_data = RechargeData.query.filter(RechargeData.app_id == app_id).first()

        if rc_data is None:
            return jsonify(operation_res_build("the rc_data does not exist", False)),

        if role != "system":
            app_ = applications_schema_single.dump(rc_data.app)
            if app_["unit_id_copy"] != identity["unit_id"]:
                raise Exception

        db.session.delete(rc_data)
        db.session.commit()
    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "a error happened in deletion")
        logger.exception(e)
        return jsonify(operation_res_build("a error happened in deletion", False))

    return jsonify(operation_res_build("deletion ok", True))


@rc_data_bp.route("/<int:app_id>", methods=["PUT"])
@role_auth_require(grant_all=True)
@log_info_record(LOG_ACTIONS["ADD"])
def rc_data_update(role, identity, app_id):
    data = request.get_json()

    rc_id = data.get("rc_id")
    rc_value = data.get("rc_value")
    rc_time = data.get("rc_time")
    photo_rc_receipt = data.get("photo_rc_receipt")
    rc_memo = data.get("rc_memo")

    try:
        rc_data = RechargeData.query.filter(RechargeData.app_id == app_id).first()

        if rc_data is None:
            return jsonify(operation_res_build("the rc_data does not exist", False)), False

        if role != "system":
            app_ = applications_schema_single.dump(rc_data.app)

            if app_["unit_id_copy"] != identity["unit_id"]:
                raise Exception

        RechargeData.query.filter(RechargeData.rc_id == rc_id). \
            update({"rc_value": rc_value, "rc_time": rc_time, "photo_rc_receipt": photo_rc_receipt, "rc_memo": rc_memo})

        db.session.commit()
    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "a  error happened in update")
        logger.exception(e)

        return jsonify(operation_res_build("a error happened in update", False)), False

    return jsonify(operation_res_build("update ok", True)), True


# 此处为photo上传借用
@rc_data_bp.route("/receipt", methods=["POST"])
@role_auth_require(grant_all=True)
@app_upload_params_check
def rc_receipt_add(role, identity, app_id, data_id, file, is_receipt):
    file_suffix = (file_name := file.filename)[file_name.rfind('.'):]

    try:
        receipt_path, attachment_path, tries = upload_preparation(current_app.config["UPLOAD_BASE_PATH"], identity["unit_id"])

        if not tries:
            return jsonify(operation_res_build("can not create folder", False))

        file_name = file_name_picker(identity["uur_id"], app_id, file_suffix)

        saved_path = join(receipt_path, file_name)

        if int(is_receipt):
            pre_sql = RechargeData.query.filter(RechargeData.rc_id == data_id)

            # 更新data表中的 票据地址
            pre_sql.update({
                "photo_rc_receipt": saved_path
            })
        else:
            return jsonify(operation_res_build("recharge app no attachment photos", True))

        file.save(saved_path)

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "a error happened in addition")
        logger.exception(e)
        return jsonify(operation_res_build("a error happened in addition", False))

    return jsonify(operation_res_build("addition ok", True))
