from os.path import join

from flask import jsonify, Blueprint, request, current_app

from models.rpPhotosModel import RpPhotos, db
from models.repairDataModel import RepairData

from schema.modelSchema import repair_data_schema_single, repair_photos_schema

from auth.identityAuth import role_auth_require, app_upload_params_check
from utils.tool import operation_res_build, upload_preparation, file_name_picker
from utils.log import log_info_record, LOG_ACTIONS
import logger

rp_photos_bp = Blueprint("rp_photos", __name__, url_prefix="/api/rp_photos")


@rp_photos_bp.route("/<int:app_id>", methods=["GET"])
@role_auth_require(grant_all=True)
def rp_photos_request(role, identity, app_id):
    try:
        rp_data = RepairData.query.filter(RepairData.app_id == app_id).first()

        if rp_data is None:
            return jsonify(operation_res_build("the rp_data does not exist", False))

        rp_data_ = repair_data_schema_single.dump(rp_data)
        rp_id = rp_data_["rp_id"]

        rp_photos = RpPhotos.query.filter(RpPhotos.rp_id == rp_id).all()
    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "a error happened in addition")
        logger.exception(e)
        return jsonify(operation_res_build("a error happened in addition", False))

    return jsonify(operation_res_build("addition ok", True), data=repair_photos_schema.dump(rp_photos))


@rp_photos_bp.route("/", methods=["POST"])
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
            pre_sql = RepairData.query.filter(RepairData.rp_id == data_id)
            saved_path = join(receipt_path, file_name)

            # 更新data表中的 票据地址
            pre_sql.update({
                "photo_rp_receipt": saved_path
            })
        else:
            saved_path = join(attachment_path, file_name)

            # 更新photo表
            rp = RpPhotos(data_id, saved_path, None)
            db.session.add(rp)

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
        return jsonify(operation_res_build("addition ok", True, pid=rp.prp_id))


@rp_photos_bp.route("/app_id/<int:app_id>", methods=["DELETE"])
@role_auth_require(grant_all=True)
@log_info_record(LOG_ACTIONS["DEL"])
def rp_photos_delete_by_app_id(role, identity, app_id):
    try:
        rp_data = RepairData.query.filter(RepairData.app_id == app_id).first()

        if rp_data is None:
            return jsonify(operation_res_build("the rp_data does not exist", False))

        rp_data_ = repair_data_schema_single.dump(rp_data)
        rp_id = rp_data_["rp_id"]

        rp_photos = RepairData.query.filter(RepairData.rp_id == rp_id).all()
        if not len(rp_photos):
            return "the rp_photos does not exist", False

        for _ in rp_photos:
            db.session.delete(_)

        db.session.commit()
    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "a error happened in deletion")
        logger.exception(e)
        return jsonify(operation_res_build("a error happened in deletion", False))

    return jsonify(operation_res_build("deletion ok", True))


@rp_photos_bp.route("/prp_id/<int:prp_id>", methods=["DELETE"])
@role_auth_require(grant_all=True)
def rp_photos_delete_by_prp_id(role, identity, prp_id):
    try:
        rp_photo = RpPhotos.query.filter(RpPhotos.prp_id == prp_id).first()
        if rp_photo is None:
            return "the rp_photo does not exist", False

        db.session.delete(rp_photo)
        db.session.commit()
    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "a error happened in deletion")
        logger.exception(e)
        return jsonify(operation_res_build("a error happened in deletion", False))

    return jsonify(operation_res_build("deletion ok", True))


@rp_photos_bp.route("/<int:prp_id>", methods=["PUT"])
@role_auth_require(grant_all=True)
def rp_photos_update(role, identity, prp_id):
    data = request.get_json()
    rp_id = data.get("rp_id")
    prp_file = data.get("prp_file")
    prp_memo = data.get("prp_memo")

    try:
        pre_sql = RpPhotos.query.filter(RpPhotos.prp_id == prp_id)
        if not len(pre_sql.first()):
            return jsonify(operation_res_build("the rp_photo does not exist", False))

        pre_sql.update({"rp_id": rp_id, "prp_file": prp_file, "prp_memo": prp_memo})

        db.session.commit()
    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "a error happened in update")
        logger.exception(e)
        return operation_res_build("a error happened in update", False)

    return operation_res_build("update ok", True)
