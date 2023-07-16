from models.common import db


class Cars(db.Model):
    __tablename__ = 'cars'

    car_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    unit_id = db.Column(db.ForeignKey('units.unit_id'), index=True)
    palte_number = db.Column(db.String(32), nullable=False)
    car_type = db.Column(db.String(32))
    car_brand = db.Column(db.String(32))
    gas_type = db.Column(db.String(16))
    tank_capacity = db.Column(db.Float)
    car_state = db.Column(db.Integer, nullable=False)
    card_number = db.Column(db.String(64), nullable=False)
    capital_balance = db.Column(db.Float, nullable=False)
    car_memo = db.Column(db.String(32))
    unit = db.relationship('Units', primaryjoin='Cars.unit_id == Units.unit_id', backref='cars')

    def __init__(self, unit_id, palte_number, car_type, car_brand, gas_type, tank_capacity, car_state,card_number, capital_balance,car_memo):
        self.unit_id = unit_id
        self.palte_number = palte_number
        self.car_type = car_type
        self.car_brand = car_brand
        self.gas_type = gas_type
        self.tank_capacity = tank_capacity
        self.car_state = car_state
        self.card_number = card_number
        self.capital_balance = capital_balance
        self.car_memo = car_memo

    def __repr__(self):
        return "class <Cars>"
