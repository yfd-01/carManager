from models.common import db


class Uurs(db.Model):
    __tablename__ = 'uurs'

    uur_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ur_id = db.Column(db.ForeignKey('units_roles.ur_id'), index=True)
    u_id = db.Column(db.ForeignKey('users.u_id'), index=True)
    unit_id_copy = db.Column(db.Integer, nullable=False)
    uur_state = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    uur_time = db.Column(db.DateTime)
    uur_memo = db.Column(db.String(128))
    u = db.relationship('Users', primaryjoin='Uurs.u_id == Users.u_id', backref='uurs')
    ur = db.relationship('UnitsRoles', primaryjoin='Uurs.ur_id == UnitsRoles.ur_id', backref='uurs')

    def __init__(self, ur_id, u_id, unit_id_copy, uur_state, uur_time, uur_memo):
        self.ur_id = ur_id
        self.u_id = u_id
        self.unit_id_copy = unit_id_copy
        self.uur_state = uur_state
        self.uur_time = uur_time
        self.uur_memo = uur_memo

    def __repr__(self):
        return "class <Uurs>"
