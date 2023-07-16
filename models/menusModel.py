from models.common import db


class Menus(db.Model):
    __tablename__ = "menus"

    menu_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    parent_menu_id = db.Column(db.ForeignKey('menus.menu_id'), index=True)
    menu_name = db.Column(db.String(32), nullable=False)
    menu_memo = db.Column(db.String(32))
    menu_path = db.Column(db.String(255))
    menu_mpath = db.Column(db.String(255))
    menu_icon = db.Column(db.String(32))

    men_menu = db.relationship('Menus', remote_side=[menu_id], primaryjoin='Menus.parent_menu_id == Menus.menu_id', backref='menus')

    def __init__(self, parent_menu_id, menu_name, menu_memo, menu_path, menu_mpath, menu_icon):
        self.parent_menu_id = parent_menu_id
        self.menu_name = menu_name
        self.menu_memo = menu_memo
        self.menu_path = menu_path
        self.menu_mpath = menu_mpath
        self.menu_icon = menu_icon

    def __repr__(self):
        return "class <Menus>"
