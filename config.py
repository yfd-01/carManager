import socket
import os

HOST = 'xxx'
PORT = '3306'
DATABASE = 'xxx'
USERNAME = 'xxx'
PASSWORD = 'xxx'

DB_URI = f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}?charset=utf8mb4"

# Flask Settings --
SQLALCHEMY_DATABASE_URI = DB_URI
SQLALCHEMY_TRACK_MODIFICATIONS = False

# SECRET_KEY = urandom(24)
# 如果这里用随机的话，在gunicorn中多进程会创建不同的SECRET_KEY，就会导致一个进程给的token不能被其余的进程所识别，从而进程越多分发的token越无效
SECRET_KEY = b'xxx'

LOGIN_FAIL_TRIES_LIMIT = 4

LOGIN_CHOOSE_TOKEN_EXIST = 300      # 角色选择前令牌存活时间，秒
ACCESS_TOKEN_EXIST = 60 * 60 * 24 * 30  # 资源访问令牌存活时间，秒
REFRESH_TOKEN_EXIST = 60 * 60 * 24 * 32  # 刷新令牌存活时间，秒

# Mail settings


MAIL_SERVER = "smtp.163.com"
MAIL_USE_TLS = True
MAIL_USERNAME = "xxx"
MAIL_PASSWORD = "xxx"
MAIL_DEFAULT_SENDER = MAIL_USERNAME

PROTOCOL = "http"
SERVER_IP = "xxx"
FRONT_PORT = "80"
PAGE_HOST = PROTOCOL + "://" + SERVER_IP + ':' + FRONT_PORT
RESET_PSW_LINK_EXIST = 60 * 60 * 3
USED_SID_DEFAULT_TIME = "1970-01-01 00:00:00"
EXPORTED_FILE_EXIST = 10 * 60

# Upload settings
PRINT_STORAGE_BASE_PATH = "static/print/"
EXPORT_STORAGE_BASE_PATH = "static/excel/"
UPLOAD_BASE_PATH = "static/upload/"
dirPath = os.path.abspath(os.path.dirname(__file__))
UPLOAD_SIGN_BASE_PATH = "sign/upload/"

APK_STORAGE_PATH = "static/apk/"

# Default Setting
# users
USER_STATE_DEFAULT = True

# units
UNIT_STATE_DEFAULT = True

# uurs
UUR_STATE_DEFAULT = True

# units_roles
UR_STATE_DEFAULT = True

# murs
MUR_STATE_DEFAULT = True


# -------
# trying to get local ip automatically
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))

SERVER_IP = s.getsockname()[0]
