import base64
import os
from os.path import join

from flask import Blueprint, jsonify, request, current_app
from models.signsModel import db, Signs
from schema.modelSchema import signs_schema_single

from auth.identityAuth import role_auth_require
import logger
from utils.tool import operation_res_build, uploaded_file_name_sign, upload_preparation_sign

signs_bp = Blueprint("signs", __name__, url_prefix="/api/signs")

# TODO - deprecated


@signs_bp.route("/", methods=["GET"])
@role_auth_require(grant_all=True)
def signs_request_by_id(role, identity):
    """
    查询签名
    :return:
    """
    try:
        sign = Signs.query.filter(Signs.u_id == identity["u_id"]).first()

        if sign is None:
            return jsonify(operation_res_build("load sign is not exist", False))

        sign = signs_schema_single.dump(sign)
        if  sign["sign_template"] is None:
            return jsonify(operation_res_build("图片不存在！", False))
        # else:
        #     data = sign["sign_template"]
        #     data = data[data.find('/')+1:]
        #     data =request.host_url+data
        #     sign["sign_template"]= data.replace("\\", '/')

        sign_file_path = sign["sign_template"]
        if os.path.exists(sign_file_path):
            encoded = base64.b64encode(open(sign_file_path, 'rb').read())
            code = 'data:;base64,'+encoded.decode("utf-8")
        else:
            return jsonify(operation_res_build("图片不存在！", False))

    except Exception as e:
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "load sign failed")
        logger.exception(e)
        return jsonify(operation_res_build("load sign failed", False))

    return jsonify(operation_res_build("load sign ok", True, sign=code))


@signs_bp.route("/", methods=["POST"])
@role_auth_require(grant_all=True)
def signs_add_or_update(role, identity):
    """
    添加或者修改签名
    :param role:
    :param identity:
    :return:
    """
    data = request.get_json()
    if not data:
        return jsonify(operation_res_build("签名不能为空！", False))
    data = data["sign"]
    data = data[data.find(",")+1:]
    img_data = base64.b64decode(data)
    # 图片存储路径
    sign_path = upload_preparation_sign(current_app.config["UPLOAD_SIGN_BASE_PATH"], identity["unit_id"])
    # 图片名字
    file_name = uploaded_file_name_sign(identity["u_id"], ".png")
    saved_path = join(sign_path, file_name)

    try:
        f = open(saved_path, "wb")
        f.write(img_data)
        f.close()
        pre_sign = Signs.query.filter(Signs.u_id == identity["u_id"])
        if pre_sign.first() is None:
            db.session.add(Signs(identity["u_id"], saved_path))
        else:

            sign = signs_schema_single.dump(pre_sign.first())
            sign_file_path = sign["sign_template"]
            # 删除已经有的签名
            if os.path.exists(sign_file_path):
                os.remove(sign_file_path)
            pre_sign.update(
                {
                    "sign_template" : saved_path
                }
            )
        db.session.commit()
    except Exception as e:
        # 失败的话就删除 传上来的图片
        if os.path.exists(saved_path):
            os.remove(saved_path)

        db.session.rollback()
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "a error happened in addition")
        logger.exception(e)
        return jsonify(operation_res_build("a error happened in addition", False))

    return jsonify(operation_res_build("addition ok", True))


@signs_bp.route("/", methods=["DELETE"])
@role_auth_require(grant_all=True)
def signs_delete(role, identity):

    try:
        pre_sign = Signs.query.filter(Signs.u_id == identity["u_id"])
        if pre_sign.first() is None:
            return jsonify(operation_res_build("签名不存在！", True))
        else:
            sign = signs_schema_single.dump(pre_sign.first())
            sign_file_path = sign["sign_template"]
            # 删除已经有的签名
            db.session.delete(pre_sign.first())
            db.session.commit()
            if os.path.exists(sign_file_path):
                os.remove(sign_file_path)
    except Exception as e:
        db.session.rollback()
        logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "a error happened in addition")
        logger.exception(e)
        return jsonify(operation_res_build("a error happened in addition", False))

    return jsonify(operation_res_build("删除成功！", True))