from functools import wraps
from flask_jwt_extended import get_jwt_identity
from flask import request

from models.logsModel import db, Logs
from utils.tool import get_current_time
from exceptions import LogRecordParamMissingError

import logger


LOG_ACTIONS = {
    "ADD": "添加",
    "DEL": "删除",
    "MOD": "修改",
    "PRINT": "打印",
    "LOGIN": "登录"
}

# 日志过滤关键字
LOG_FILTER_KEY = ["passwd", "oldpass", "pass", "checkPass"]


def log_info_record(log_operation):
    def wrapper(view_func):
        @wraps(view_func)
        def decorator(*args, **kwargs):
            try:
                identity = get_jwt_identity()

                resp, flag = view_func(*args, **kwargs)
            except TypeError:
                raise LogRecordParamMissingError

            try:
                db.session.add(Logs(identity["uur_id"], identity["unit_id"], get_current_time(), log_operation,
                                    log_content_build(request.url), login_content_filter(request.get_json(silent=True)), flag))
                db.session.commit()
            except Exception as e:
                logger.error(request.environ.get('HTTP_X_REAL_IP', request.remote_addr), "a error happened in log")
                logger.exception(e)

            return resp

        return decorator

    return wrapper


def log_content_build(url):
    url_ = url[url.find("/api"):]

    return url_


def login_content_filter(values):
    if values is None:
        return None

    val = dict(values)
    for _ in LOG_FILTER_KEY:
        try:
            del val[_]
        except KeyError:
            pass

    return str(val)[: 512]
