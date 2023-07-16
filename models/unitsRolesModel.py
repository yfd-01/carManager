from models.common import db


class UnitsRoles(db.Model):
    __tablename__ = 'units_roles'

    ur_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    unit_id = db.Column(db.ForeignKey('units.unit_id'), index=True)
    role_id = db.Column(db.ForeignKey('roles.role_id'), index=True)
    ur_state = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    ur_time = db.Column(db.DateTime)
    unit_name_copy = db.Column(db.String(32))
    role_name_copy = db.Column(db.String(32))
    ur_memo = db.Column(db.String(64))

    role = db.relationship('Roles', primaryjoin='UnitsRoles.role_id == Roles.role_id', backref='units_roles')
    unit = db.relationship('Units', primaryjoin='UnitsRoles.unit_id == Units.unit_id', backref='units_roles')

    def __init__(self, unit_id, role_id, ur_state, ur_time, unit_name_copy, role_name_copy, ur_memo):
        self.unit_id = unit_id
        self.role_id = role_id
        self.ur_state = ur_state
        self.ur_time = ur_time
        self.unit_name_copy = unit_name_copy
        self.role_name_copy = role_name_copy
        self.ur_memo = ur_memo

    def __repr__(self):
        return "class <UnitsRoles>"
