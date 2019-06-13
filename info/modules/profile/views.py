from flask import render_template, g

from info.utils.common import user_login
from info.modules.profile import profile_blu


@profile_blu.route("/user_base_info")
@user_login
def user_base_info():
    """
    渲染基本资料页面
    :return:
    """
    user = g.user

    data = {
        "user_info":user.to_dict()
    }

    return render_template("news/user_base_info.html", data=data)


@profile_blu.route("/info")
@user_login
def user_info():
    """
    个人中心
    :return:
    """
    user = g.user

    if not user:
        return credits("/")

    data = {
        "user_info":user.to_dict()
    }

    return render_template("/news/user.html", data=data)