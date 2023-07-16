# 认证错误基类
class AuthError(Exception):
    pass


# 日志错误基类
class LogError(Exception):
    pass


# 认证消息定义不匹配异常
class AuthMsgDefNoMatchError(AuthError):
    def __init__(self):
        pass

    def __str__(self):
        return "the definitions between CLAIM and CODE set are not matchable"


# 认证角色不存在异常
class AuthRolesIsNotExisted(AuthError):
    def __init__(self, auth_role):
        self.auth_role = auth_role

    def __str__(self):
        return f"the auth role that you require is not defined, check out { self.auth_role }"


# 认证角色传入类型异常
class AuthRolesTypeError(AuthError):
    def __init__(self, auth_role):
        self.auth_role = auth_role

    def __str__(self):
        return f"the auth role that you require should be a `List` instead of { type(self.auth_role) }"


# 认证角色传入参数异常
class AuthRolesParamError(AuthError):
    def __init__(self, **kwargs):
        self.param = kwargs

    def __str__(self):
        return f"params is invalid { self.param }"


class LogRecordParamMissingError(LogError):
    def __init__(self):
        pass

    def __str__(self):
        return "you have to specify operation result, which means there is a value of flag"

