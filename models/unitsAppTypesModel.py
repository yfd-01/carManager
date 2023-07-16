from models.common import db


class UnitsApptypes(db.Model):
    __tablename__ = 'units_apptypes'

    ua_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    unit_id = db.Column(db.ForeignKey('units.unit_id'), index=True)
    type_id = db.Column(db.ForeignKey('apptypes.type_id'), index=True)
    # 对应申请的文档模板的地址
    ua_template = db.Column(db.String(128))
    ua_state = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    ua_memo = db.Column(db.String(64))

    type = db.relationship('AppTypes', primaryjoin='UnitsApptypes.type_id == AppTypes.type_id',
                           backref='units_apptypes')
    unit = db.relationship('Units', primaryjoin='UnitsApptypes.unit_id == Units.unit_id', backref='units_apptypes')

    def __init__(self, unit_id, type_id, ua_template, ua_state, ua_memo, ):
        self.unit_id = unit_id
        self.type_id = type_id
        self.ua_template = ua_template
        self.ua_state = ua_state
        self.ua_memo = ua_memo

    def __repr__(self):
        return "class <UnitsApptypes>"
