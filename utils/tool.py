import math
import os
import datetime
import random
import time
import hashlib
from random import choices

from auth.msgDef import ROLE_NAME_ROLE_ID_REFLECTION


def get_current_time(format="%Y-%m-%d %H:%M:%S"):
    """
    得到当前时间
    """

    return time.strftime(format, time.localtime())


def get_time_gap(new_t, old_t):
    """
    得到时间间隔
    """

    if not isinstance(new_t, str) or not isinstance(old_t, str):
        raise TypeError

    new_t = new_t.replace('T', ' ', 1)
    old_t = old_t.replace('T', ' ', 1)

    return str(
        datetime.datetime.strptime(new_t, "%Y-%m-%d %H:%M:%S") - datetime.datetime.strptime(old_t, "%Y-%m-%d %H:%M:%S"))


def get_time_offset(offset_time_h):
    """
    得到当前时间的偏移
    """

    return (datetime.datetime.now() + datetime.timedelta(hours=offset_time_h)).strftime("%Y-%m-%d %H:%M:%S")


def remove_T_char_in_time_str(t):
    """
    去除时间中的‘T’字符
    """

    if not isinstance(t, str):
        raise TypeError

    return t.replace('T', ' ', 1)


def operation_res_build(msg, flag, **kwargs):
    """
    拼接返回消息
    """

    return {"msg": msg, "flag": flag, **kwargs}


def usr_psw_generator(passwd):
    """
    用户密码密文生成
    """

    sha512 = hashlib.sha512()
    sha512.update(passwd.encode())

    _ = sha512.hexdigest()
    _l = _[: 64]
    _r = _[64:]

    _ = _r + _l
    _ = _[: 32] + ''.join(reversed(_[32: 96])) + _[96:]

    return _


def auth_role_exclude(*args):
    """
    返回除目标角色之外的全部角色
    """

    role_name_ls = list(ROLE_NAME_ROLE_ID_REFLECTION.keys())

    for ex_role in args:
        role_name_ls.remove(ex_role)

    return role_name_ls


# ----Deprecated
# def allowed_file(filename):
#     return '.' in filename and \
#            filename.rsplit('.', 1)[1].lower() in current_app.config["ALLOWED_EXTENSIONS"]


def random_chars_gen(len_, ignore_capital=True):
    """
    生成随机字符
    """

    content = '2345689abcdefghijkmnpqrstuvwxyzABCDEFGHJKMNPQRSTUVWXYZ'

    if ignore_capital:
        return "".join(choices(content, k=len_)).lower()
    else:
        return "".join(choices(content, k=len_))


def logging_content_assemble(url, json_):
    return f'{url[url.find("/api"):]} - {"" if json_ is None else json_}'


def upload_preparation(upload_base_path, unit_id):
    ym = time.strftime("%Y-%m", time.localtime())
    ym_unit_path = os.path.join(upload_base_path, ym, str(unit_id))

    receipt_path = os.path.join(ym_unit_path, "receipt")
    attachment_path = os.path.join(ym_unit_path, "attachment")

    tries = 10
    while not os.path.exists(receipt_path) or not os.path.exists(attachment_path):
        try:
            os.makedirs(receipt_path)
            os.makedirs(attachment_path)
            time.sleep(0)
        except FileExistsError:
            pass
        finally:
            tries -= 1

        if not tries:
            break

    return receipt_path, attachment_path, tries


def upload_preparation_sign(upload_base_path, unit_id):
    sign_path = os.path.join(upload_base_path, str(unit_id) + '/')
    if not os.path.exists(sign_path):
        os.makedirs(sign_path)

    return sign_path


def file_name_picker(uur_id, app_id, file_suffix):
    return f"{uur_id}_{app_id}_{time.time()}{file_suffix}"


def uploaded_file_name_sign(uur_id, file_suffix):
    return f"{uur_id}_{random.randint(1,100000)}_{int(time.time())}{file_suffix}"


def long_word_split(word, split_len):
    try:
        return [word[i*split_len: (i+1)*split_len] for i in range(math.ceil(len(word) / split_len))]
    except Exception:
        return []

# def delete_data_photo_preparation(app_type_copy, app):
#     if app_type_copy == "maintaindata":
#         data_set = app.maintaindata
#         data_schema_single_specify = maintain_data_schema_single
#         photo_schema_single_specify = mt_photos_schema_single
#         photo_receipt_specify = "photo_mt_receipt"
#         photo_attachment_specify = "pmt_file"
#         model_specify = MaintainData
#
#     elif app_type_copy == "rechargedata":
#         data_set = app.rechargedata
#         data_schema_single_specify = recharge_data_schema_single
#         photo_schema_single_specify = None
#         photo_receipt_specify = "photo_rc_receipt"
#         photo_attachment_specify = None
#         model_specify = RechargeData
#
#     elif app_type_copy == "repairdata":
#         data_set = app.repairdata
#         data_schema_single_specify = repair_data_schema_single
#         photo_schema_single_specify = repair_photos_schema_single
#         photo_receipt_specify = "photo_rp_receipt"
#         photo_attachment_specify = "prp_file"
#         model_specify = RepairData
#
#     elif app_type_copy == "refueldata":
#         data_set = app.refueldata
#         data_schema_single_specify = refuel_data_schema_single
#         photo_schema_single_specify = refuel_photos_schema_single
#         photo_receipt_specify = "photo_ref_receipt"
#         photo_attachment_specify = "prf_file"
#         model_specify = RefuelData
#     else:
#         return False, (None, None, None, None, None, None)
#
#     return True, (data_set, data_schema_single_specify,
#                   photo_schema_single_specify, photo_receipt_specify, photo_attachment_specify, model_specify)
