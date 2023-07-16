from flask_marshmallow import Marshmallow

from models.applicationsModel import Applications
from models.apptypesModel import AppTypes
from models.carsModel import Cars
from models.flowsModel import Flows
from models.logsModel import Logs
from models.maintainDataModel import MaintainData
from models.menusModel import Menus
from models.mtPhotosModel import MtPhotos
from models.mursModel import Murs
from models.rechargeDataModel import RechargeData
from models.refuelDataModel import RefuelData
from models.rentsModel import Rents
from models.repairDataModel import RepairData
from models.rfPhotosModel import RfPhotos
from models.rolesModel import Roles
from models.rpPhotosModel import RpPhotos
from models.signsModel import Signs
from models.unitsModel import Units
from models.unitsRolesModel import UnitsRoles
from models.usersModel import Users
from models.uursModel import Uurs
from models.unitsAppTypesModel import UnitsApptypes
from models.settingsModel import Settings

ma = Marshmallow()


# 申请 -------------------------------
class ApplicationsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Applications
        include_fk = True


applications_schema = ApplicationsSchema(many=True)
applications_schema_single = ApplicationsSchema()


# 申请类型 -------------------------------
class AppTypesSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = AppTypes


app_types_schema = AppTypesSchema(many=True)
app_types_schema_single = AppTypesSchema()


# 车辆 -------------------------------
class CarsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Cars
        include_fk = True


cars_schema = CarsSchema(many=True)
cars_schema_single = CarsSchema()


# 流程 -------------------------------
class FlowsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Flows
        include_fk = True


flows_schema = FlowsSchema(many=True)
flows_schema_single = FlowsSchema()


# 日志 -------------------------------
class LogsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Logs
        include_fk = True


logs_schema = LogsSchema(many=True)
logs_schema_single = LogsSchema()


# 保养 -------------------------------
class MaintainDataSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = MaintainData
        include_fk = True


maintain_data_schema = MaintainDataSchema(many=True)
maintain_data_schema_single = MaintainDataSchema()


# 菜单 -------------------------------
class MenusSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Menus
        include_fk = True


menus_schema = MenusSchema(many=True)
menus_schema_single = MenusSchema()


# 保养图片 -------------------------------
class MtPhotosSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = MtPhotos
        include_fk = True


maintain_photos_schema = MtPhotosSchema(many=True)
maintain_photos_schema_single = MtPhotosSchema()


# 角色菜单 -------------------------------
class MursSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Murs
        include_fk = True


murs_schema = MursSchema(many=True)
murs_schema_single = MursSchema()


# 充值 -------------------------------
class RechargeDataSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = RechargeData
        include_fk = True


recharge_data_schema = RechargeDataSchema(many=True)
recharge_data_schema_single = RechargeDataSchema()


# 加油 -------------------------------
class RefuelDataSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = RefuelData
        include_fk = True


refuel_data_schema = RefuelDataSchema(many=True)
refuel_data_schema_single = RefuelDataSchema()


# 加油图片 -------------------------------
class RfPhotosSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = RfPhotos
        include_fk = True


refuel_photos_schema = RfPhotosSchema(many=True)
refuel_photos_schema_single = RfPhotosSchema()


# 订阅 -------------------------------
class RentsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Rents
        include_fk = True


rents_schema = RentsSchema(many=True)
rents_schema_single = RentsSchema()


# 维修 -------------------------------
class RepairDataSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = RepairData
        include_fk = True


repair_data_schema = RepairDataSchema(many=True)
repair_data_schema_single = RepairDataSchema()


# 维修图片 -------------------------------
class RpPhotosSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = RpPhotos
        include_fk = True


repair_photos_schema = RpPhotosSchema(many=True)
repair_photos_schema_single = RpPhotosSchema()


# 角色 -------------------------------
class RolesSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Roles


roles_schema = RolesSchema(many=True)
roles_schema_single = RolesSchema()


# 签名 -------------------------------
class SignsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Signs
        include_fk = True


signs_schema = SignsSchema(many=True)
signs_schema_single = SignsSchema()


# 公司 -------------------------------
class UnitsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Units
        include_fk = True


units_schema = UnitsSchema(many=True)
units_schema_single = UnitsSchema()


# 公司-角色 -------------------------------
class UnitsRolesSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = UnitsRoles
        include_fk = True


units_roles_schema = UnitsRolesSchema(many=True)
units_roles_schema_single = UnitsRolesSchema()


# 用户 -------------------------------
class UsersSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Users


users_schema = UsersSchema(many=True)
users_schema_single = UsersSchema()


# 用户-公司-角色 -------------------------------
class UursSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Uurs
        include_fk = True


uurs_schema = UursSchema(many=True)
uurs_schema_single = UursSchema()


# 公司和申请类型---------------------------
class UnitsApptypesSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = UnitsApptypes
        include_fk = True


units_app_types_schema = UnitsApptypesSchema(many=True)
units_app_types_schema_single = UnitsApptypesSchema()


# mt照片---------------------------
class MtPhotoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = MtPhotos


mt_photos_schema = MtPhotoSchema(many=True)
mt_photos_schema_single = MtPhotoSchema()


class SettingsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Settings


settings_schema = SettingsSchema(many=True)
settings_schema_single = SettingsSchema()
