from models.common import db


class RepairData(db.Model):
    __tablename__ = 'repairdata'

    rp_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    app_id = db.Column(db.ForeignKey('applications.app_id'), index=True)
    # 维修项目
    rp_item = db.Column(db.String(256), nullable=False)
    # 维修金额，不需要从油卡中剔除
    rp_cost = db.Column(db.Float, nullable=False)
    # 维修时间
    rp_time = db.Column(db.DateTime)
    # 地点
    rp_addr = db.Column(db.String(128))
    # 维修时公里数
    rp_mile = db.Column(db.Float)
    # 图片
    photo_rp_receipt = db.Column(db.String(128))
    rp_memo = db.Column(db.String(256))

    app = db.relationship('Applications', primaryjoin='RepairData.app_id == Applications.app_id', backref='repairdata')

    def __init__(self, app_id, rp_item, rp_cost, rp_time, rp_addr, rp_mile, photo_rp_receipt, rp_memo):
        self.app_id = app_id
        self.rp_item = rp_item
        self.rp_cost = rp_cost
        self.rp_time = rp_time
        self.rp_addr = rp_addr
        self.rp_mile = rp_mile
        self.photo_rp_receipt = photo_rp_receipt
        self.rp_memo = rp_memo

    def __repr__(self):
        return "class <RepairData>"

