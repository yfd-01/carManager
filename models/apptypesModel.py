from models.common import db


class AppTypes(db.Model):
    __tablename__ = 'apptypes'

    type_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type_name = db.Column(db.String(32), nullable=False)
    type_memo = db.Column(db.String(32))

    def __init__(self, type_name, type_memo):
        self.type_name = type_name
        self.type_memo = type_memo

    def __repr__(self):
        return "class <Apptypes>"
