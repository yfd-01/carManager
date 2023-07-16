"""
@File  :get_model.py
@Author:AixLeon
@Date  :2022/5/221:36
@Desc  :
"""
from models.maintainDataModel import MaintainData
from models.rechargeDataModel import RechargeData
from models.refuelDataModel import RefuelData
from models.repairDataModel import RepairData
from models.mtPhotosModel import MtPhotos

from models.rpPhotosModel import RpPhotos
from models.rfPhotosModel import RfPhotos

from schema.modelSchema import refuel_data_schema_single, maintain_data_schema_single, \
    repair_data_schema_single, maintain_photos_schema, repair_photos_schema, refuel_photos_schema_single, \
    maintain_photos_schema_single,repair_photos_schema_single,recharge_data_schema_single


def get_model(type_name):
    model = {}
    if type_name == "maintaindata":
        model["Model"] = MaintainData
        model["Model_schema_single"] = maintain_data_schema_single
        model["Photos"] = MtPhotos
        model["Photos_schema_single"] = maintain_photos_schema_single
        model["Photos_schema"] = maintain_photos_schema
        model["receipt"] = "photo_mt_receipt"
        model["photo_key"] = MtPhotos.pmt_id
        model["file_path"] = "pmt_file"

    elif type_name == "rechargedata":
        model["Model"] = RechargeData
        model["Model_schema_single"] = recharge_data_schema_single
        model["Photos"] = None
        model["Photos_schema_single"] = None
        model["Photos_schema"] = None
        model["receipt"] = "photo_rc_receipt"
        model["photo_key"] = None
        model["file_path"] = None

    elif type_name == "refueldata":
        model["Model"] = RefuelData
        model["Model_schema_single"] = refuel_data_schema_single
        model["Photos"] = RfPhotos
        model["Photos_schema_single"] = refuel_photos_schema_single
        model["Photos_schema"] = repair_photos_schema
        model["receipt"] = "photo_ref_receipt"
        model["photo_key"] = RfPhotos.prf_id
        model["file_path"] = "prf_file"

    elif type_name == "repairdata":
        model["Model"] = RepairData
        model["Model_schema_single"] = repair_data_schema_single
        model["Photos"] = RpPhotos
        model["Photos_schema_single"] = repair_photos_schema_single
        model["Photos_schema"] = repair_photos_schema
        model["receipt"] = "photo_rp_receipt"
        model["photo_key"] = RpPhotos.prp_id
        model["file_path"] = "prp_file"
    return model

