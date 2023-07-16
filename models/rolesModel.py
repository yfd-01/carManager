from models.common import db


class Roles(db.Model):
    __tablename__ = 'roles'

    role_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    role_name = db.Column(db.String(32), nullable=False)
    role_memo = db.Column(db.String(128))
    # unitroles = db.relationship('UnitsRoles',backref='roles',lazy='dynamic')

    def __init__(self, role_name, role_memo=None):
        self.role_name = role_name
        self.role_memo = role_memo

    def __repr__(self):
        return "class <Roles>"
