from flask import render_template, request, current_app, session

from info.modules.admin import admin_blu
from info.models import User


@admin_blu.route("/login", methods=["GET", "POST"])
def login():
    """
    后台管理员登录页面
    :return:
    """
    if request.method == "GET":
        return render_template("admin/login.html")

    username = request.form.get("username")
    password = request.form.get("password")

    if not all([username, password]):
        return render_template("admin/login.html", errmsg="请输入用户名或密码")
    try:
        user = User.query.filter(User.is_admin==1, User.mobile==username).first()
    except Exception as e:
        current_app.logger.error(e)
        return render_template("admin/login.html", errmsg="用户信息查询失败")
    if not user:
        return render_template("admin/login.html", errmsg="未查到用户信息")
    if not user.check_passowrd(password):
        return render_template("admin/login.html", errmsg="用户名或密码错误")

    session["user_id"] = user.id
    session["is_admin"] = user.is_admin

    return "登录成功"