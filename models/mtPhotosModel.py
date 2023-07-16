from models.common import db


class MtPhotos(db.Model):
    __tablename__ = 'mtphotos'

    pmt_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    mt_id = db.Column(db.ForeignKey('maintaindata.mt_id'), index=True)
    pmt_file = db.Column(db.String(128), nullable=False)
    pmt_memo = db.Column(db.String(32))

    mt = db.relationship('MaintainData', primaryjoin='MtPhotos.mt_id == MaintainData.mt_id', backref='mtphotos')

    def __init__(self, mt_id, pmt_file, pmt_memo):
        self.mt_id = mt_id
        self.pmt_file = pmt_file
        self.pmt_memo = pmt_memo

    def __repr__(self):
        return "class <MtPhotos>"
