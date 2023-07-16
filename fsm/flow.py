class Flow:
    STATES_SET = {
        "DRAFT_APP":            1,       # 起草申请
        "OFFICER_REVIEW":       2,       # 待干部审核
        "LEADER_REVIEW":        3,       # 待领导批准
        "INFO_UPLOAD":          4,       # 待上传资料
        "INFO_CHECK":           5,       # 待查验资料
        "FULFILL_INFO":         6,       # 待完善资料
        "REJECT_APP":           7,       # 申请被驳回
        "WITHDRAW":             8,       # 撤回
        "DONE":                 9        # 结束
    }

    EVENTS_SET = {
        "SUBMIT":               1,       # 提交
        "OFFICER_APPROVAL":     2,       # 干部批准
        "LEADER_APPROVAL":      3,       # 领导批准
        "UPLOAD_INFO":          4,       # 上传资料
        "LEADER_PASS":          5,       # 干部审核通过
        "OFFICER_DISMISS":      6,       # 干部驳回
        "LEADER_DISMISS":       7,       # 领导驳回
        "MODIFIED_SUBMIT":      8,       # 员工修改后提交
        "STAFF_WITHDRAW":       9,       # 员工撤回
        "STAFF_UPDATE_INFO":    10,      # 员工更新资料
        "LEADER_PASS_FAIL":     11,      # 干部查验未通过
        "APP_DONE_BACK":        12,      # 完成申请回退
        "EMERGENCY_APP_FLY":    13,      # 紧急申请发出
    }

    FSMTable = (
        (STATES_SET["DRAFT_APP"],       EVENTS_SET["SUBMIT"],               "submit"),
        (STATES_SET["OFFICER_REVIEW"],  EVENTS_SET["OFFICER_APPROVAL"],     "officer_approval"),
        (STATES_SET["OFFICER_REVIEW"],  EVENTS_SET["OFFICER_DISMISS"],      "officer_dismiss"),
        (STATES_SET["LEADER_REVIEW"],   EVENTS_SET["LEADER_APPROVAL"],      "leader_approval"),
        (STATES_SET["LEADER_REVIEW"],   EVENTS_SET["LEADER_DISMISS"],       "leader_dismiss"),
        (STATES_SET["INFO_UPLOAD"],     EVENTS_SET["UPLOAD_INFO"],          "upload_info"),
        (STATES_SET["INFO_CHECK"],      EVENTS_SET["LEADER_PASS"],          "leader_pass"),
        (STATES_SET["INFO_CHECK"],      EVENTS_SET["LEADER_PASS_FAIL"],     "leader_pass_fail"),
        (STATES_SET["REJECT_APP"],      EVENTS_SET["MODIFIED_SUBMIT"],      "modified_submit"),
        (STATES_SET["REJECT_APP"],      EVENTS_SET["STAFF_WITHDRAW"],       "staff_withdraw"),
        (STATES_SET["FULFILL_INFO"],    EVENTS_SET["STAFF_UPDATE_INFO"],    "staff_update_info"),
        (STATES_SET["DONE"],            EVENTS_SET["APP_DONE_BACK"],        "app_done_back"),
        (STATES_SET["DRAFT_APP"],       EVENTS_SET["EMERGENCY_APP_FLY"],    "emergency_app_fly"),
    )

    def __init__(self):
        pass

    def __repr__(self):
        return "class <Flow>"

    def step(self, cur_state, active_event):
        for _ in self.FSMTable:
            if _[0] == cur_state and _[1] == active_event:
                new_state, new_state_depict = eval(f"self.{_[2]}")

                return {"new_state": new_state, "new_state_depict": new_state_depict,
                        "_events": self.get_events_by_status(new_state)}

        return None

    def trans_state(self, _s):
        return list(self.STATES_SET.keys())[_s - 1]

    def trans_event(self, _e):
        return list(self.EVENTS_SET.keys())[_e - 1]

    def get_events_by_status(self, cur_status):
        return [(fsm[1], fsm[2]) for fsm in self.FSMTable if fsm[0] == cur_status]

    @property
    def submit(self):
        return self.STATES_SET["OFFICER_REVIEW"], "OFFICER_REVIEW"

    @property
    def officer_approval(self):
        return self.STATES_SET["LEADER_REVIEW"], "LEADER_REVIEW"

    @property
    def officer_dismiss(self):
        return self.STATES_SET["REJECT_APP"], "REJECT_APP"

    @property
    def leader_approval(self):
        return self.STATES_SET["INFO_UPLOAD"], "INFO_UPLOAD"

    @property
    def leader_dismiss(self):
        return self.STATES_SET["REJECT_APP"], "REJECT_APP"

    @property
    def upload_info(self):
        return self.STATES_SET["INFO_CHECK"], "INFO_CHECK"

    @property
    def leader_pass(self):
        return self.STATES_SET["DONE"], "DONE"

    @property
    def leader_pass_fail(self):
        return self.STATES_SET["FULFILL_INFO"], "FULFILL_INFO"

    @property
    def modified_submit(self):
        return self.STATES_SET["OFFICER_REVIEW"], "OFFICER_REVIEW"

    @property
    def staff_withdraw(self):
        return self.STATES_SET["WITHDRAW"], "WITHDRAW"

    @property
    def staff_update_info(self):
        return self.STATES_SET["INFO_CHECK"], "INFO_CHECK"

    @property
    def app_done_back(self):
        return self.STATES_SET["INFO_UPLOAD"], "INFO_UPLOAD"

    @property
    def emergency_app_fly(self):
        return self.STATES_SET["INFO_UPLOAD"], "INFO_UPLOAD"

# f = Flow()
# f.trans_state(2)
