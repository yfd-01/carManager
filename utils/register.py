from blueprint.users import users_bp
from blueprint.roles import roles_bp
from blueprint.units import units_bp
from blueprint.unitsRoles import units_roles_bp
from blueprint.uurs import uurs_bp
from blueprint.rents import rents_bp

from blueprint.logs import logs_bp
from blueprint.signs import signs_bp

from blueprint.cars import cars_bp
from blueprint.unitsAppTypes import units_app_types_bp
from blueprint.apptypes import app_types_bp

from blueprint.flows import flows_bp
from blueprint.applications import applications_bp

from blueprint.maintainData import mt_data_bp
from blueprint.rechargeData import rc_data_bp
from blueprint.refuelData import ref_data_bp
from blueprint.repairData import rp_data_bp

from blueprint.mtPhotos import mt_photos_bp
from blueprint.rfPhotos import rf_photos_bp
from blueprint.rpPhotos import rp_photos_bp

from blueprint.menus import menus_bp
from blueprint.murs import murs_bp

from blueprint.settings import settings_bp
from blueprint.apk import apk_bp

from auth.genCaptcha import captcha_bp


def register_bps(app):
    """
    统一路由注册
    """

    app.register_blueprint(users_bp)
    app.register_blueprint(roles_bp)
    app.register_blueprint(units_bp)
    app.register_blueprint(units_roles_bp)
    app.register_blueprint(uurs_bp)
    app.register_blueprint(rents_bp)

    app.register_blueprint(logs_bp)
    app.register_blueprint(signs_bp)

    app.register_blueprint(cars_bp)
    app.register_blueprint(units_app_types_bp)
    app.register_blueprint(app_types_bp)

    app.register_blueprint(flows_bp)
    app.register_blueprint(applications_bp)

    app.register_blueprint(mt_data_bp)
    app.register_blueprint(rc_data_bp)
    app.register_blueprint(ref_data_bp)
    app.register_blueprint(rp_data_bp)

    app.register_blueprint(mt_photos_bp)
    app.register_blueprint(rf_photos_bp)
    app.register_blueprint(rp_photos_bp)

    app.register_blueprint(murs_bp)
    app.register_blueprint(menus_bp)
    app.register_blueprint(captcha_bp)

    app.register_blueprint(settings_bp)
    app.register_blueprint(apk_bp)
