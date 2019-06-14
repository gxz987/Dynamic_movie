from flask import render_template

from info.modules.admin import admin_blu


@admin_blu.route("/login")
def login():
    """
    后台管理员登录页面
    :return:
    """
    return render_template("admin/login.html")