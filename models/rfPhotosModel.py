from models.common import db


class RfPhotos(db.Model):
    __tablename__ = 'rfphotos'

    prf_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ref_id = db.Column(db.ForeignKey('refueldata.ref_id'), index=True)
    prf_file = db.Column(db.String(128), nullable=False)
    prf_memo = db.Column(db.String(64))

    ref = db.relationship('RefuelData', primaryjoin='RfPhotos.ref_id == RefuelData.ref_id', backref='rfphotos')

    def __init__(self, ref_id, prf_file, prf_memo):
        self.ref_id = ref_id
        self.prf_file = prf_file
        self.prf_memo = prf_memo

    def __repr__(self):
        return "class <RfPhotos>"
