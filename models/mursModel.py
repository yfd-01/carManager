from models.common import db


class Murs(db.Model):
    __tablename__ = "murs"

    mur_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    menu_id = db.Column(db.ForeignKey('menus.menu_id'), index=True)
    ur_id = db.Column(db.ForeignKey('units_roles.ur_id'), index=True)
    mur_state = db.Column(db.Boolean, nullable=False, default=True)
    mur_memo = db.Column(db.String(32))

    ur = db.relationship('UnitsRoles', primaryjoin='Murs.ur_id == UnitsRoles.ur_id', backref='murs')
    menu = db.relationship('Menus', primaryjoin='Murs.menu_id == Menus.menu_id', backref='murs')

    def __init__(self, menu_id, ur_id, mur_state, mur_memo):
        self.menu_id = menu_id
        self.ur_id = ur_id
        self.mur_state = mur_state
        self.mur_memo = mur_memo

    def __repr__(self):
        return "class <Murs>"

