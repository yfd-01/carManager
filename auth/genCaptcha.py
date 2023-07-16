from flask import Blueprint, make_response, session

from captcha.image import ImageCaptcha
from PIL import Image
from io import BytesIO

from utils.tool import random_chars_gen


def __gen_captcha():
    """
    生成验证码
    """
    image = ImageCaptcha()
    # 获取字符串
    captcha_text = random_chars_gen(len_=4)
    # 生成图像
    captcha_image = Image.open(image.generate(captcha_text))

    return captcha_text, captcha_image


captcha_bp = Blueprint("captcha", __name__, url_prefix="/api/captcha")


@captcha_bp.route("/")
def get_captcha():
    """
    生成验证码图像
    """
    str_, img = __gen_captcha()

    buf = BytesIO()
    img.save(buf, 'jpeg')
    buf_str = buf.getvalue()

    resp = make_response(buf_str)
    resp.headers['Content-Type'] = 'image/gif'

    session['captcha'] = str_

    return resp
