from models.common import db



class RechargeData(db.Model):
    __tablename__ = 'rechargedata'

    rc_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 申请id
    app_id = db.Column(db.ForeignKey('applications.app_id'), index=True)
    # 充值金额
    rc_value = db.Column(db.Float, nullable=False)
    # 充值时间
    rc_time = db.Column(db.DateTime, nullable=False)
    # 充值票据
    photo_rc_receipt = db.Column(db.String(128))
    # 备注
    rc_memo = db.Column(db.String(64))

    app = db.relationship('Applications', primaryjoin='RechargeData.app_id == Applications.app_id',
                          backref='rechargedata')

    def __init__(self, app_id, rc_value, rc_time, photo_rc_receipt, rc_memo):
        self.app_id = app_id
        self.rc_value = rc_value
        self.photo_rc_receipt = photo_rc_receipt
        self.rc_time = rc_time
        self.rc_memo = rc_memo

    def __repr__(self):
        return "class <RechargeData>"
