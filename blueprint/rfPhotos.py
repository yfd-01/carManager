from os.path import join

from flask import jsonify, Blueprint, request, current_app

from models.rfPhotosModel import RfPhotos, db
from models.refuelDataModel import RefuelData

from schema.modelSchema import refuel_photos_schema, refuel_data_schema_single
from auth.identityAuth import role_auth_require, app_upload_params_check
from utils.log import LOG_ACTIONS, log_info_record

from utils.tool import operation_res_build, upload_preparation, file_name_picker
import logger

rf_photos_bp = Blueprint("rf_photos", __name__, url_prefix="/api/rf_photos")


@rf_photos_bp.route("/<int:app_id>", methods=["GET"])
@role_auth_require(grant_all=True)
def rf_photos_request(role, identity, app_id):
    try:
        ref_data = RefuelData.query.filter(RefuelData.app_id == app_id).first()

        if ref_data is None:
            return jsonify(operation_res_build("the ref_data does not exist", False))

        ref_data_ = refuel_data_schema_single.dump(ref_data)
        ref_id = ref_data_["ref_id"]

        rf_photos = RfPhotos.query.filter(RfPhotos.ref_id == ref_id).all()
    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "a error happened in addition")
        logger.exception(e)
        return jsonify(operation_res_build("a error happened in addition", False))

    return jsonify(operation_res_build("addition ok", True), data=refuel_photos_schema.dump(rf_photos))


@rf_photos_bp.route("/", methods=["POST"])
@role_auth_require(grant_all=True)
@app_upload_params_check
def rf_photos_add(role, identity, app_id, data_id, file, is_receipt):
    file_suffix = (file_name := file.filename)[file_name.rfind('.'):]

    try:
        receipt_path, attachment_path, tries = upload_preparation(current_app.config["UPLOAD_BASE_PATH"], identity["unit_id"])

        if not tries:
            return jsonify(operation_res_build("can not create folder", False))

        file_name = file_name_picker(identity["uur_id"], app_id, file_suffix)

        if int(is_receipt):
            pre_sql = RefuelData.query.filter(RefuelData.ref_id == data_id)
            saved_path = join(receipt_path, file_name)

            # 更新data表中的 票据地址
            pre_sql.update({
                "photo_ref_receipt": saved_path
            })
        else:
            saved_path = join(attachment_path, file_name)

            # 更新photo表
            rf = RfPhotos(data_id, saved_path, None)
            db.session.add(rf)

        file.save(saved_path)

        db.session.flush()
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "a error happened in addition")
        logger.exception(e)
        return jsonify(operation_res_build("a error happened in addition", False))

    if int(is_receipt):
        return jsonify(operation_res_build("addition ok", True))
    else:
        return jsonify(operation_res_build("addition ok", True, pid=rf.prf_id))


@rf_photos_bp.route("/app_id/<int:app_id>", methods=["DELETE"])
@role_auth_require(grant_all=True)
@log_info_record(LOG_ACTIONS["DEL"])
def rf_photos_delete_by_app_id(role, identity, app_id):
    try:
        ref_data = RefuelData.query.filter(RefuelData.app_id == app_id).first()

        if ref_data is None:
            return jsonify(operation_res_build("the ref_data does not exist", False)), False

        ref_data_ = refuel_data_schema_single.dump(ref_data)
        ref_id = ref_data_["ref_id"]

        rf_photos = RfPhotos.query.filter(RfPhotos.ref_id == ref_id).all()
        if not len(rf_photos):
            return "the rf_photos does not exist", False

        for _ in rf_photos:
            db.session.delete(_)

        db.session.commit()
    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "a error happened in deletion")
        logger.exception(e)
        return jsonify(operation_res_build("a error happened in deletion", False)), False

    return jsonify(operation_res_build("deletion ok", True)), False


@rf_photos_bp.route("/prf_id/<int:prf_id>", methods=["DELETE"])
@role_auth_require(grant_all=True)
@log_info_record(LOG_ACTIONS["DEL"])
def rf_photos_delete_by_prf_id(role, identity, prf_id):
    try:
        rf_photo = RfPhotos.query.filter(RfPhotos.prf_id == prf_id).first()
        if rf_photo is None:
            return "the rf_photo does not exist", False

        db.session.delete(rf_photo)
        db.session.commit()
    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "a error happened in deletion")
        logger.exception(e)
        return jsonify(operation_res_build("a error happened in deletion", False)), False

    return jsonify(operation_res_build("deletion ok", True)), True


@rf_photos_bp.route("/<int:prf_id>", methods=["PUT"])
@role_auth_require(grant_all=True)
@log_info_record(LOG_ACTIONS["MOD"])
def rf_photos_update(role, identity, prf_id):
    data = request.get_json()

    ref_id = data.get("ref_id")
    prf_file = data.get("prf_file")
    prf_memo = data.get("prf_memo")

    try:
        pre_sql = RfPhotos.query.filter(RfPhotos.prf_id == prf_id)
        if not len(pre_sql.first()):
            return jsonify(operation_res_build("the rf_photo does not exist", False)), False

        pre_sql.update({"ref_id": ref_id, "prf_file": prf_file, "prf_memo": prf_memo})

        db.session.commit()
    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "a error happened in update")
        logger.exception(e)
        return operation_res_build("a error happened in update", False), False

    return operation_res_build("update ok", True), True

