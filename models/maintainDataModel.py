from models.common import db


class MaintainData(db.Model):
    __tablename__ = 'maintaindata'

    mt_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 申请id
    app_id = db.Column(db.ForeignKey('applications.app_id'), index=True)
    # 保养内容
    mt_item = db.Column(db.String(256), nullable=False)
    # 保养地址
    mt_addr = db.Column(db.String(128))
    # 保养时间
    mt_time = db.Column(db.DateTime)
    # 保养开销 不需要从油卡里减除
    mt_cost = db.Column(db.Float, nullable=False)
    # 保养时的总里程
    mt_mile = db.Column(db.Float)
    # 保养单据，必须要有的。
    photo_mt_receipt = db.Column(db.String(128))
    # 保养备注
    mt_memo = db.Column(db.String(128))

    app = db.relationship('Applications', primaryjoin='MaintainData.app_id == Applications.app_id',
                          backref='maintaindata')

    def __init__(self, app_id, mt_item, mt_addr, mt_time, mt_cost, mt_mile, photo_mt_receipt, mt_memo):
        self.app_id = app_id
        self.mt_item = mt_item
        self.mt_addr = mt_addr
        self.mt_time = mt_time
        self.mt_cost = mt_cost
        self.mt_mile = mt_mile
        self.photo_mt_receipt = photo_mt_receipt
        self.mt_memo = mt_memo

    def __repr__(self):
        return "class <MaintainData>"
