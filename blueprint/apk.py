import os
import time
from flask import Blueprint, jsonify, request, current_app

from utils.tool import operation_res_build
from auth.identityAuth import role_auth_require

apk_bp = Blueprint("apk", __name__, url_prefix="/api/apk")


@apk_bp.route("/upload", methods=["POST"])
@role_auth_require(auth_roles=["system"])
def apk_upload(role, identity):
    if role != "system":
        return jsonify(operation_res_build("only system manager can upload newest apk", False))

    file_apk = request.files.getlist("file")[0]
    if file_apk is None:
        return jsonify(operation_res_build("no file content in uploading", False))

    if file_apk.filename.endswith(".apk"):
        _path = current_app.config["APK_STORAGE_PATH"]
        if not os.path.exists(_path):
            os.mkdir(_path)
            time.sleep(0)

        file_apk.save(os.path.join(_path, "apk_release.apk"))
    else:
        return jsonify(operation_res_build("illegal suffix", False))

    return jsonify(operation_res_build("new version apk has been saved", True))
