from models.common import db


class Settings(db.Model):
    __tablename__ = 'settings'

    set_id = db.Column(db.Integer, primary_key=True)
    app_refresh = db.Column(db.Integer)
    app_version = db.Column(db.String(32))

    def __init__(self, set_id, app_refresh, app_version):
        self.set_id = set_id
        self.app_refresh = app_refresh
        self.app_version = app_version

    def __repr__(self):
        return "class <Settings>"
