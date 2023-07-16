from models.common import db


class Units(db.Model):
    __tablename__ = 'units'

    # 单位id
    unit_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    parent_unit_id = db.Column(db.ForeignKey('units.unit_id'), index=True)

    # 单位名称
    unit_name = db.Column(db.String(32), nullable=False)
    unit_address = db.Column(db.String(128))
    unit_contact = db.Column(db.String(32))
    unit_tel = db.Column(db.String(32))
    rent_expiretime = db.Column(db.DateTime, nullable=False)

    # 注册时间
    unit_regtime = db.Column(db.DateTime, nullable=False)

    # 单位状态
    unit_state = db.Column(db.Integer, nullable=False, default=True)
    unit_memo = db.Column(db.String(32))

    uni_unit = db.relationship('Units', remote_side=[unit_id], primaryjoin='Units.parent_unit_id == Units.unit_id', backref='units')

    def __init__(self, parent_unit_id, unit_name, unit_address, unit_contact, unit_tel, rent_expiretime,
                 unit_regtime, unit_state, unit_memo=None):
        self.parent_unit_id = parent_unit_id
        self.unit_name = unit_name
        self.unit_address = unit_address
        self.unit_contact = unit_contact
        self.unit_tel = unit_tel
        self.rent_expiretime = rent_expiretime
        self.unit_regtime = unit_regtime
        self.unit_state = unit_state
        self.unit_memo = unit_memo

    def __repr__(self):
        return "class <Units>"
