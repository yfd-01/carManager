from flask import Flask
from flask_cors import CORS

from models.common import db
from auth.identityAuth import jwt
from utils.register import register_bps
from utils.mail import mail

import config

app = Flask(__name__)
app.config.from_object(config)  # 应用基本设置导入

CORS(app, supports_credentials=True)    # 跨域设置

db.init_app(app)    # 数据库关联
jwt.init_app(app)   # jwt关联
register_bps(app)   # 路由蓝图注册
mail.init_app(app)

if __name__ == "__main__":
    app.run(host=config.SERVER_IP,
            port=3000)
