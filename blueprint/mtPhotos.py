from os.path import join

from flask import jsonify, Blueprint, request, current_app

from models.mtPhotosModel import MtPhotos, db
from models.maintainDataModel import MaintainData

from schema.modelSchema import maintain_data_schema_single, mt_photos_schema
from auth.identityAuth import role_auth_require, app_upload_params_check
from utils.log import log_info_record, LOG_ACTIONS
from utils.tool import operation_res_build, upload_preparation, file_name_picker

import logger

mt_photos_bp = Blueprint("mt_photos", __name__, url_prefix="/api/mt_photos")


@mt_photos_bp.route("/<int:app_id>", methods=["GET"])
@role_auth_require(grant_all=True)
def mt_photos_request(role, identity, app_id):
    try:
        mt_data = MaintainData.query.filter(MaintainData.app_id == app_id).first()

        if mt_data is None:
            return jsonify(operation_res_build("the mt_data does not exist", False))

        mt_data_ = maintain_data_schema_single.dump(mt_data)
        mt_id = mt_data_["mt_id"]

        mt_photos = MtPhotos.query.filter(MtPhotos.mt_id == mt_id).all()
    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "a error happened in addition")
        logger.exception(e)
        return jsonify(operation_res_build("a error happened in addition", False))

    return jsonify(operation_res_build("addition ok", True), data=mt_photos_schema.dump(mt_photos))


@mt_photos_bp.route("/", methods=["POST"])
@role_auth_require(grant_all=True)
@app_upload_params_check
def mt_photos_add(role, identity, app_id, data_id, file, is_receipt):
    file_suffix = (file_name := file.filename)[file_name.rfind('.'):]

    try:
        receipt_path, attachment_path, tries = upload_preparation(current_app.config["UPLOAD_BASE_PATH"], identity["unit_id"])

        if not tries:
            return jsonify(operation_res_build("can not create folder", False))

        file_name = file_name_picker(identity["uur_id"], app_id, file_suffix)

        if int(is_receipt):
            pre_sql = MaintainData.query.filter(MaintainData.mt_id == data_id)
            saved_path = join(receipt_path, file_name)

            # 更新data表中的 票据地址
            pre_sql.update({
                "photo_mt_receipt": saved_path
            })
        else:
            saved_path = join(attachment_path, file_name)

            # 更新photo表
            mt = MtPhotos(data_id, saved_path, None)
            db.session.add(mt)

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
        return jsonify(operation_res_build("addition ok", True, pid=mt.pmt_id))


# 推荐使用该方式删除
@mt_photos_bp.route("/app_id/<int:app_id>", methods=["DELETE"])
@role_auth_require(grant_all=True)
@log_info_record(LOG_ACTIONS["DEL"])
def mt_photos_delete_by_app_id(role, identity, app_id):
    try:
        mt_data = MaintainData.query.filter(MaintainData.app_id == app_id).first()

        if mt_data is None:
            return jsonify(operation_res_build("the mt_data does not exist", False))

        mt_data_ = maintain_data_schema_single.dump(mt_data)
        mt_id = mt_data_["mt_id"]

        mt_photos = MtPhotos.query.filter(MtPhotos.mt_id == mt_id).all()
        if not len(mt_photos):
            return "the mt_photos does not exist", False

        for _ in mt_photos:
            db.session.delete(_)

        db.session.commit()
    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "a error happened in deletion")
        logger.exception(e)
        return jsonify(operation_res_build("a error happened in deletion", False))

    return jsonify(operation_res_build("deletion ok", True))


@mt_photos_bp.route("/pmt_id/<int:pmt_id>", methods=["DELETE"])
@role_auth_require(grant_all=True)
@log_info_record(LOG_ACTIONS["DEL"])
def mt_photos_delete_by_pmt_id(role, identity, pmt_id):
    try:
        mt_photo = MtPhotos.query.filter(MtPhotos.pmt_id == pmt_id).first()
        if mt_photo is None:
            return "the mt_photo does not exist", False

        db.session.delete(mt_photo)
        db.session.commit()
    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "a error happened in deletion")
        logger.exception(e)
        return jsonify(operation_res_build("a error happened in deletion", False)), False

    return jsonify(operation_res_build("deletion ok", True)), True


@mt_photos_bp.route("/<int:pmt_id>", methods=["PUT"])
@role_auth_require(grant_all=True)
@log_info_record(LOG_ACTIONS["MOD"])
def mt_photos_update(role, identity, pmt_id):
    data = request.get_json()

    mt_id = data.get("mt_id")
    pmt_file = data.get("pmt_file")
    pmt_memo = data.get("pmt_memo")

    try:
        pre_sql = MtPhotos.query.filter(MtPhotos.pmt_id == pmt_id)
        if not len(pre_sql.first()):
            return jsonify(operation_res_build("the mt_photo does not exist", False)), False

        pre_sql.update({"mt_id": mt_id, "pmt_file": pmt_file, "pmt_memo": pmt_memo})

        db.session.commit()
    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "a error happened in update")
        logger.exception(e)
        return operation_res_build("a error happened in update", False), False

    return operation_res_build("update ok", True), True
