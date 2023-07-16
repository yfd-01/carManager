from models.common import db


# 申请和审批流程的详细记录
class Flows(db.Model):
    __tablename__ = 'flows'

    flowstate_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 申请id
    app_id = db.Column(db.ForeignKey('applications.app_id'), index=True)
    # 公司与user
    uur_id = db.Column(db.ForeignKey('uurs.uur_id'), index=True)

    # 当前状态的名称
    flowstate_title = db.Column(db.String(32))
    # 在本状态的操作
    flowstate_event = db.Column(db.String(32), nullable=False)

    flowstate_time = db.Column(db.DateTime, nullable=False)
    # 耗时。 本操作 时间减去上个状态的时间
    flowstate_spendtime = db.Column(db.String(16))
    # 操作者 ，角色 【姓名 】，从 roles表 和users 表复制
    operator_role_name_copy = db.Column(db.String(32))
    # 审批意见和员工反馈
    comment = db.Column(db.String(128))

    app = db.relationship('Applications', primaryjoin='Flows.app_id == Applications.app_id', backref='flows')
    uur = db.relationship('Uurs', primaryjoin='Flows.uur_id == Uurs.uur_id', backref='flows')

    def __init__(self, app_id, uur_id, unit_id_copy, flowstate_title, flowstate_event, flowstate_time, flowstate_spendtime,
                 operator_role_name_copy, comment):
        self.app_id = app_id
        self.uur_id = uur_id
        self.unit_id_copy = unit_id_copy
        self.flowstate_title = flowstate_title
        self.flowstate_event = flowstate_event
        self.flowstate_time = flowstate_time
        self.flowstate_spendtime = flowstate_spendtime
        self.operator_role_name_copy = operator_role_name_copy
        self.comment = comment

    def __repr__(self):
        return "class <Flows>"
