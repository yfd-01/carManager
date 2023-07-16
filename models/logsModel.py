from models.common import db


class Logs(db.Model):
    __tablename__ = 'logs'

    log_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uur_id = db.Column(db.ForeignKey('uurs.uur_id'), index=True)
    unit_id_copy = db.Column(db.Integer, nullable=False)
    log_time = db.Column(db.DateTime)
    # 操作：增加 删除 修改 打印
    log_operation = db.Column(db.String(8), nullable=False)
    log_url = db.Column(db.String(256))
    log_content = db.Column(db.String(512))
    operation_res = db.Column(db.Integer)

    uur = db.relationship('Uurs', primaryjoin='Logs.uur_id == Uurs.uur_id', backref='logs')

    def __init__(self, uur_id, unit_id_copy, log_time, log_operation, log_url, log_content, operation_res):
        self.uur_id = uur_id
        self.unit_id_copy = unit_id_copy
        self.log_time = log_time
        self.log_operation = log_operation
        self.log_url = log_url
        self.log_content = log_content
        self.operation_res = operation_res

    def __repr__(self):
        return "class <Logs>"
