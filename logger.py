import logging.config
import logging

# logging模块配置加载
logging.config.fileConfig("logging.conf")
# logger生成
app_logger = logging.getLogger("appLogger")


def debug(ip, msg):
    app_logger.debug(f"{ip} | {msg}")


def info(ip, msg):
    app_logger.info(f"{ip} | {msg}")


def warning(ip, msg):
    app_logger.warning(f"{ip} | {msg}")


def error(ip, msg):
    app_logger.error(f"{ip} | {msg}")


def critical(ip, msg):
    app_logger.critical(f"{ip} | {msg}")


def exception(e):
    app_logger.exception(e)
