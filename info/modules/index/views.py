from flask import render_template, redirect, current_app, send_file, session, request, jsonify, g

from info import constants
from info.utils.common import user_login
from info.modules.index import index_blu
from info.models import User, News, Category
from info.utils.response_code import RET


@index_blu.route("/news_list")
def get_news_list():
    """
    显示新闻列表，因是局部刷新，需要用jsonify返回数据故更改接口
    1、接收参数 cid(f分类id,必须)  page  per_page
    2、校验参数是否合法
    3、查询出新闻（要关系分类）（根据创建时间排序）
    4、返回响应，及新闻数据
    :return:
    """
    # 1、接收参数
    cid = request.args.get("cid")
    page = request.args.get("page", 1)
    per_page = request.args.get("per_page", 10)

    # 2.校验数据
    try:
        cid = int(cid)
        page = int(page)
        per_page = int(per_page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 3、查询数据库
    filters = [News.status == 0]
    if cid != 1:
        filters.append(News.category_id==cid)
    try:
        paginate = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page, per_page, False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询错误")

    news_list = paginate.items   # 当前页数据
    current_page = paginate.page    # 当前页数
    total_page = paginate.pages  # 总页数

    news_dict_li = [news.to_basic_dict() for news in news_list]
    data = {
        "news_dict_li":news_dict_li,
        "news_page":current_page,
        "total_page":total_page
    }

    return jsonify(errno=RET.OK, errmsg="OK", data=data)




@index_blu.route('/')
@user_login
def index():
    # 首页右上角的实现
    # 进入首页，需要判断用户是否登录，若已登录，将用户信息显示
    user = g.user

    # 1.显示新闻的点击排行
    clicks_news = []
    try:
        clicks_news = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS) # [news1, news2,...]
    except Exception as e:
        current_app.logger.error(e)

    clicks_news_li = [news.to_basic_dict() for news in clicks_news]

    # 2.显示新闻分类
    categorys = []

    try:
        categorys = Category.query.all()
    except Exception as e:
        current_app.logger.error(e)

    categorys_dict_li = [category.to_dict() for category in categorys]
    # data = {"user_info":{"nick_name":"guo"}}
    data = {
        "user_info":user.to_dict() if user else None,
        "clicks_news_li":clicks_news_li,
        "categorys_dict_li":categorys_dict_li
    }

    return render_template("news/index.html", data=data)


@index_blu.route('/favicon.ico')
def favicon():
    # 返回logn图片
    # 第一种方法：
    # return redirect("/static/news/favicon.ico")  # 有302重定向问题

    # 第二种方法
    return current_app.send_static_file("news/favicon.ico")
    # send_static_file(filename)
    # Function used internally to send static files from the static
    # folder to the browser.

    # 第三种方法
    # return send_file("static/news/favicon.ico")
