from flask import render_template, g, request, jsonify, current_app

from info import db, constants
from info.utils.common import user_login
from info.modules.profile import profile_blu
from info.libs.image_storage import storage
from info.models import Category, News
from info.utils.response_code import RET


@profile_blu.route("/user_follow")
@user_login
def user_follow():
    """我的关注"""
    page = request.args.get("page", 1)
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    user = g.user
    follows = []
    current_page = 1
    total_page = 1
    try:
        paginate = user.followed.paginate(page, constants.USER_FOLLOWED_MAX_COUNT, False)
        follows = paginate.items
        current_page = paginate.page
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)

    user_dict_li = [follow_user.to_dict() for follow_user in follows]

    data = {
        "users": user_dict_li,
        "current_page": current_page,
        "total_page": total_page
    }

    return render_template("news/user_follow.html", data=data)


@profile_blu.route('/user_news_list')
@user_login
def user_news_list():
    """
    用户新闻列表
    :return:
    """
    user = g.user
    page = request.args.get("page")

    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    news_li = []
    current_page = 1
    total_page = 1

    try:
        paginate = News.query.filter(News.user_id==user.id).paginate(page, constants.USER_COLLECTION_MAX_NEWS, False)
        news_li = paginate.items
        current_page = paginate.page
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.eror(e)

    news_dict_li = [news.to_review_dict() for news in news_li]
    data = {
        "news_dict_li":news_dict_li,
        "current_page":current_page,
        "total_page":total_page
    }
    print(news_dict_li)
    return render_template("news/user_news_list.html", data=data)




@profile_blu.route("/user_news_release", methods=["GET", "POST"])
@user_login
def user_news_release():
    """
    用户发布新闻
    :return:
    """
    user = g.user
    if request.method == "GET":
        categories = []
        try:
            categories = Category.query.all()
        except Exception as e:
            current_app.logger.error(e)
        categories_dict_li = [category.to_dict() for category in categories]
        categories_dict_li.pop(0)
        data = {
            "categories_dict_li":categories_dict_li
        }
        return render_template("news/user_news_release.html", data=data)

    title = request.form.get("title")
    category_id = request.form.get("category_id")
    digest = request.form.get("digest")
    index_image = request.files.get("index_image")
    content = request.form.get("content")

    if not all([title, category_id, digest, index_image, content]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")
    try:
        category_id = int(category_id)
        image_data = index_image.read()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    try:
        key = storage(image_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="第三方上传失败")

    # 执行业务逻辑
    news= News()
    news.title = title
    news.source = "个人发布"
    news.digest = digest
    news.content = content
    news.index_image_url = constants.QINIU_DOMIN_PREFIX + key
    news.category_id = category_id
    news.user_id = user.id
    news.status = 1
    print(news)
    try:
        db.session.add(news)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库保存失败")

    return jsonify(errno=RET.OK,errmsg="OK")


@profile_blu.route("/user_collection")
@user_login
def user_collection():
    """
    显示用户收藏的新闻
    :return:
    """
    user = g.user
    page = request.args.get("page")
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    # 查询该用户收藏的新闻
    news_list = []
    current_page = 1
    total_page = 1
    try:
        paginate = user.collection_news.paginate(page, constants.USER_COLLECTION_MAX_NEWS, False)
        news_list = paginate.items
        current_page = paginate.page
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)

    news_dict_li = [news.to_dict() for news in news_list]

    data = {
        "news_dict_li":news_dict_li,
        "current_page":current_page,
        "total_page":total_page
    }

    return render_template("news/user_collection.html", data=data)


@profile_blu.route("/user_pass_info", methods=["GET", "POST"])
@user_login
def user_pass_info():
    """
    密码修改
    :return:
    """
    user = g.user
    if request.method == "GET":
        return render_template("news/user_pass_info.html")

    old_password = request.json.get("old_password")
    new_password = request.json.get("new_password")

    if not all([old_password, new_password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    if not user.check_passowrd(old_password):
        return jsonify(errno=RET.DATAERR, errmsg="旧密码输入错误")

    user.password = new_password
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库保存失败")

    return jsonify(errno=RET.OK, errmsg="密码修改成功")


@profile_blu.route("/user_pic_info", methods=["GET", "POST"])
@user_login
def user_pic_info():
    """
    用户头像设置
    :return:
    """
    user = g.user
    if request.method == "GET":
        data = {
            "user_info":user.to_dict()
        }
        return render_template("news/user_pic_info.html", data=data)

    try:
        image_data = request.files.get("avatar").read()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 将用户上传的图像保存在七牛云上
    try:
        key = storage(image_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="上传头像失败")

    user.avatar_url = key
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库保存失败")

    return jsonify(errno=RET.OK, errmsg="上传头像成功", data=constants.QINIU_DOMIN_PREFIX + key)


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