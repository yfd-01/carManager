from flask_mail import Message, Mail
from flask import current_app

mail = Mail()


def send_mail(recipient, sid):
    try:
        href = f"{current_app.config['PAGE_HOST']}/#/general/changepsw?sid={sid}"
        msg = Message("油料管理系统-密码重置", recipients=[recipient])
        msg.html = f"<span>请点击以下链接重置密码，3小时内有效<span/><br/>" \
                   f"<a href='{href}'>{href}</a>"

        mail.send(msg)
    except Exception:
        return False

    return True
