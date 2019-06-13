from flask import render_template, g, request, jsonify, current_app

from info import db
from info.utils.common import user_login
from info.modules.profile import profile_blu
from response_code import RET


@profile_blu.route("/user_pic_info", methods=["GET", "POST"])
@user_login
def user_pic_info():
    """
    用户头像设置
    :return:
    """
    user = g.user
    data = {
        "user_info":user.to_dict()
    }
    return render_template("news/user_pic_info.html", data=data)




@profile_blu.route("/user_base_info", methods=["GET", "POST"])
@user_login
def user_base_info():
    """
    渲染基本资料页面
    :return:
    """
    user = g.user
    # 个人基本资料的显示
    if request.method == "GET":
        data = {
            "user_info":user.to_dict()
        }
        return render_template("news/user_base_info.html", data=data)

    #
    nick_name = request.json.get("nick_name")
    signature = request.json.get("signature")
    gender = request.json.get("gender")

    if not all([nick_name, signature, gender]):
        return  jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    if gender not in ["MAN", "WOMAN"]:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 修改该用户的用户名 签名 性别
    user.nick_name = nick_name
    user.signature = signature
    user.gender = gender
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库保存失败")
    return jsonify(errno=RET.OK, errmsg="OK", data=user.to_dict())


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