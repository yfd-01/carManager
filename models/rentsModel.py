from models.common import db


class Rents(db.Model):
    __tablename__ = 'rents'

    #租户id
    rent_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    #单位id
    unit_id = db.Column(db.ForeignKey('units.unit_id'), index=True)
    #租借时间
    rent_time = db.Column(db.DateTime, nullable=False)

    rent_length = db.Column(db.String(32), nullable=False)

    rent_value = db.Column(db.Float, nullable=False)

    rent_memo = db.Column(db.String(128))

    unit = db.relationship('Units', primaryjoin='Rents.unit_id == Units.unit_id', backref='rents')

    def __init__(self, unit_id, rent_time, rent_length, rent_value, rent_memo):
        self.unit_id = unit_id
        self.rent_time = rent_time
        self.rent_length = rent_length
        self.rent_value = rent_value
        self.rent_momo = rent_memo

    def __repr__(self):
        return "class <Rents>"

