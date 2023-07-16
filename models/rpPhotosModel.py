from models.common import db


class RpPhotos(db.Model):
    __tablename__ = 'rpphotos'

    prp_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    rp_id = db.Column(db.ForeignKey('repairdata.rp_id'), index=True)
    prp_file = db.Column(db.String(128), nullable=False)
    prp_memo = db.Column(db.String(32))

    rp = db.relationship('RepairData', primaryjoin='RpPhotos.rp_id == RepairData.rp_id', backref='rpphotos')

    def __init__(self, rp_id, prp_file, prp_memo):
        self.rp_id = rp_id
        self.prp_file = prp_file
        self.prp_memo = prp_memo

    def __repr__(self):
        return "class <RpPhotos>"
