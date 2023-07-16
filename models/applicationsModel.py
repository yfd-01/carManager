from models.common import db


class Applications(db.Model):
    __tablename__ = 'applications'

    app_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uur_id = db.Column(db.ForeignKey('uurs.uur_id'), index=True)
    type_id = db.Column(db.ForeignKey('apptypes.type_id'), index=True)
    car_id = db.Column(db.ForeignKey('cars.car_id'), index=True)
    name_copy = db.Column(db.String(32), nullable=False)
    type_name_copy = db.Column(db.String(32), nullable=False)
    app_quick = db.Column(db.Integer, nullable=False)
    unit_id_copy = db.Column(db.Integer, nullable=False)
    app_sheet = db.Column(db.String(128))
    app_time_start = db.Column(db.DateTime)
    app_time_end = db.Column(db.DateTime)
    flowstate_title_copy = db.Column(db.String(32), nullable=False)
    flowstate_time_copy = db.Column(db.DateTime)
    ur_id = db.Column(db.Integer)
    app_memo = db.Column(db.String(256))

    car = db.relationship('Cars', primaryjoin='Applications.car_id == Cars.car_id', backref='applications')
    type = db.relationship('AppTypes', primaryjoin='Applications.type_id == AppTypes.type_id', backref='applications')
    uur = db.relationship('Uurs', primaryjoin='Applications.uur_id == Uurs.uur_id', backref='applications')

    def __init__(self, uur_id, type_id, car_id, name_copy, type_name_copy, app_quick, unit_id_copy, app_sheet, app_time_start,
                 app_time_end, flowstate_title_copy, flowstate_time_copy, ur_id, app_memo):
        self.uur_id = uur_id
        self.type_id = type_id
        self.car_id = car_id
        self.name_copy = name_copy
        self.type_name_copy = type_name_copy
        self.app_quick = app_quick
        self.unit_id_copy = unit_id_copy
        self.app_sheet = app_sheet
        self.app_time_start = app_time_start
        self.app_time_end = app_time_end
        self.flowstate_title_copy = flowstate_title_copy
        self.flowstate_time_copy = flowstate_time_copy
        self.ur_id = ur_id
        self.app_memo = app_memo

    def __repr__(self):
        return "class <Applications>"
