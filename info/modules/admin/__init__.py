from flask import Blueprint


admin_blu = Blueprint("admin", __name__, url_prefix="/admin")


from .views import *


@admin_blu.before_request
def admin_identification():
    """
    进入后台之前的校验
    :return:
    """
    # 我先从你的session获取下is_admin 如果能获取到 说明你是管理员
    # 如果访问的接口是/admin/login 那么可以直接访问
    is_login = request.url.endswith("/login")  # 判断请求的url是否以/login结尾，即登录页面
    is_admin = session.get("is_admin")  # 判断用户是否是管理员
    if not is_admin and not is_login:
        return redirect("/")
