from models.common import db


class RefuelData(db.Model):
    __tablename__ = 'refueldata'

    ref_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 申请id
    app_id = db.Column(db.ForeignKey('applications.app_id'), index=True)
    # 是否给本车加油。不是要填写备注
    ref_self = db.Column(db.Integer, nullable=False)
    # 单价/升
    ref_price = db.Column(db.Float, nullable=False)
    # 加油量/升
    ref_volume = db.Column(db.Float, nullable=False)
    # 油金 额/元 。从加油卡扣除
    ref_cost = db.Column(db.Float, nullable=False)
    capital_balance_copy = db.Column(db.Float)
    # 剩余油量刻度 比如 1/3
    ref_remainder = db.Column(db.String(16))
    # 加油后油量刻度
    ref_finished_scale = db.Column(db.String(16))
    # 加油时间
    ref_time = db.Column(db.DateTime)
    # 加油地点
    ref_addr = db.Column(db.String(128))
    # 加油标号
    ref_gas_type = db.Column(db.String(16))
    # 加油时的里程表/公里
    ref_mile = db.Column(db.Float)
    # 照片
    photo_ref_receipt = db.Column(db.String(128))
    ref_memo = db.Column(db.String(128))

    app = db.relationship('Applications', primaryjoin='RefuelData.app_id == Applications.app_id', backref='refueldata')

    def __init__(self, app_id, ref_self, ref_price, ref_volume, ref_cost, capital_balance_copy, ref_remainder,
                 ref_finished_scale, ref_time, ref_addr, ref_gas_type, ref_mile, photo_ref_receipt, ref_memo):
        self.app_id = app_id
        self.ref_self = ref_self
        self.ref_price = ref_price
        self.ref_volume = ref_volume
        self.ref_cost = ref_cost
        self.capital_balance_copy = capital_balance_copy
        self.ref_remainder = ref_remainder
        self.ref_finished_scale = ref_finished_scale
        self.ref_time = ref_time
        self.ref_addr = ref_addr
        self.ref_gas_type = ref_gas_type
        self.ref_mile = ref_mile
        self.photo_ref_ceceipt = photo_ref_receipt
        self.ref_memo = ref_memo

    def __repr__(self):
        return "class <RefuelData>"
