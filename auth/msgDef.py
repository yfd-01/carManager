# Definition Of Auth Msg
from exceptions import AuthMsgDefNoMatchError
import config
import pymysql

# 令牌错误消息定义
CLAIM = {
    "MISS":         "the interface requires a carried token in the request",
    "INVALID":      "your carried token has signature verification failure",
    "EXPIRED":      "your carried token has expired",
    "NO_RIGHT":     "the identity you have provided is not enough to access this resource",
    "INACTIVE":     "can not find a active status in this uur_id, it may affected by changing of role",
}

# 令牌错误码定义
CODE = {
    "MISS":         101,
    "INVALID":      102,
    "EXPIRED":      103,
    "NO_RIGHT":     104,
    "INACTIVE":     105,
}

if CLAIM.keys() != CODE.keys():
    raise AuthMsgDefNoMatchError

# 角色关系映射
ROLE_NAME_ROLE_ID_REFLECTION = {}
ROLE_ID_ROLE_NAME_REFLECTION = {}

ROLE_ID_ROLE_MEMO_REFLECTION = {}

# 申请类型关系映射
TYPE_NAME_TYPE_MEMO_REFLECTION = {}
# TYPE_MEMO_TYPE_NAME_REFLECTION = {}
TYPE_ID_TYPE_NAME_REFLECTION = {}
TYPE_NAME_TYPE_ID_REFLECTION = {}

# 菜单数据读入 - {1: {}}
MENU_INFO = {}

try:
    conn = pymysql.connect(
        host=config.HOST,
        user=config.USERNAME,
        password=config.PASSWORD,
        database=config.DATABASE,
        charset="utf8"
    )

    cur = conn.cursor()
    cur.execute("SELECT role_id, role_name, role_memo FROM roles;")

    for role in cur.fetchall():
        ROLE_NAME_ROLE_ID_REFLECTION[role[1]] = role[0]
        ROLE_ID_ROLE_NAME_REFLECTION[role[0]] = role[1]
        ROLE_ID_ROLE_MEMO_REFLECTION[role[0]] = role[2]

    print("【INFO】 角色映射导入成功")

    cur.execute("SELECT type_id, type_name, type_memo FROM apptypes;")

    for type_ in cur.fetchall():
        TYPE_NAME_TYPE_MEMO_REFLECTION[type_[1]] = type_[2]
        # TYPE_MEMO_TYPE_NAME_REFLECTION[type_[2]] = type_[1]
        TYPE_ID_TYPE_NAME_REFLECTION[type_[0]] = type_[1]
        TYPE_NAME_TYPE_ID_REFLECTION[type_[1]] = type_[0]

    print("【INFO】 申请类型关系映射导入成功")

    cur.execute("SELECT menu_id, parent_menu_id, menu_name, menu_memo, menu_path, menu_icon, menu_mpath FROM menus;")
    for menu in cur.fetchall():
        MENU_INFO[menu[0]] = {
            "menu_id": menu[0],
            "parent_menu_id": menu[1],
            "menu_name": menu[2],
            "menu_memo": menu[3],
            "menu_path": menu[4],
            "menu_icon": menu[5],
            "menu_mpath": menu[6]
        }

    print("【INFO】 菜单基本信息导入成功")

    conn.close()
except pymysql.err.MySQLError:
    print("【ERROR】 映射导入失败")
    exit(-9)


# 垂直权限操作码定义
FIELD_CODE = {
    "PASS": 200,        # 垂直权限检测通过
    "INVALID": 201,     # unit id提供格式错误
    "NO_RIGHT": 202,    # 垂直权限检测不通过
    "SERVER_ERR": 203,  # 数据库查询失败
}
