from models.common import db


class Users(db.Model):
    __tablename__ = 'users'

    # 用户id
    u_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 手机号
    mobile = db.Column(db.String(15), nullable=False)
    # 姓名
    name = db.Column(db.String(32), nullable=False)
    # 密码
    passwd = db.Column(db.String(128), nullable=False)
    # 账号状态
    user_state = db.Column(db.Boolean, nullable=False, default=True)
    # 用户签名地址
    user_sign = db.Column(db.String(128))

    user_memo = db.Column(db.String(64))

    user_mail = db.Column(db.String(64))
    findpass_duetime = db.Column(db.DateTime)
    findpass_random = db.Column(db.String(64))

    failtimes = db.Column(db.Integer)

    def __init__(self, mobile, name, passwd, user_state, user_sign=None, user_memo=None, user_mail=None,
                 findpass_duetime=None, findpass_random=None, failtimes=0):
        self.mobile = mobile
        self.name = name
        self.passwd = passwd
        self.user_state = user_state
        self.user_sign = user_sign
        self.user_memo = user_memo
        self.user_mail = user_mail
        self.findpass_duetime = findpass_duetime
        self.findpass_random = findpass_random
        self.failtimes = failtimes

    def __repr__(self):
        return "class <Users>"
