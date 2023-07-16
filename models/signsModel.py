from models.common import db


class Signs(db.Model):
    __tablename__ = 'signs'

    sign_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    u_id = db.Column(db.ForeignKey('users.u_id'), index=True)
    sign_template = db.Column(db.String(128), nullable=False)
    u = db.relationship('Users', primaryjoin='Signs.u_id == Users.u_id', backref='signs')

    def __init__(self, u_id, sign_template):
        self.u_id = u_id
        self.sign_template = sign_template

    def __repr__(self):
        return "class <Signs>"
