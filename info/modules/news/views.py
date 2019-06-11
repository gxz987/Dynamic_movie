from flask import render_template, session, current_app, g, abort, jsonify, request

from info import constants, db
from info.utils.common import user_login
from info.modules.news import news_blu
from info.models import News, User, Comment
from response_code import RET


@news_blu.route("/news_comment", methods=["POST"])
@user_login
def set_news_comment():
    """
    新闻评论
    1.接收参数：new_id(必须), comment(必须), parent_id(非必须)
    2.校验参数
    3.初始化一个评论模型，并赋值
    4.返回相应，把相关评论返回及评论数
    :return:
    """
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")
    # 1.接收参数
    news_id = request.json.get("news_id")
    comment_str = request.json.get("comment")
    parent_id = request.json.get("parent_id")

    # 2.判断参数
    if not all([news_id, comment_str]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    try:
        news_id = int(news_id)
        if parent_id:
            parent_id = int(parent_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 3.查询新闻，并判断新闻是否存在
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询错误")
    if not news:
        return jsonify(errno=RET.NODATA, errmsg="未查询到新闻数据")

    # 4.初始化一个评论模型，并赋值
    comment = Comment()
    comment.user_id = user.id
    comment.news_id = news_id
    comment.content = comment_str
    try:
        db.session.add(comment)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库保存失败")

    # 查询出该条新闻下的评论条数
    comment_count = Comment.query.filter(Comment.news_id == news_id).count()

    return jsonify(errno=RET.OK, errmsg="OK", data=comment.to_dict(), comment_count=comment_count)



@news_blu.route("/news_collect", methods=["POST"])
@user_login
def news_collect():
    """
    新闻收藏和取消收藏功能的实现
    1.接收参数 news_id  action
    2.校验参数
    3.收藏新闻和取消收藏
    4.返回响应
    :return:
    """
    user = g.user

    if not user:
        return jsonify(error=RET.SESSIONERR, errmsg="用户未登录")

    news_id = request.json.get("news_id")
    action = request.json.get("action")

    if not all([news_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    if action not in ['collect', 'cancel_collect']:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    try:
        news_id = int(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数格式不正确")

    # 查询数据库
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询错误")

    if not news:
        return jsonify(errno=RET.NODATA, errmsg="该条新闻不存在")

    # 代码运行到这时，用户存在、新闻也存在
    # 执行具体的业务逻辑
    if action == "collect":
        # 收藏新闻时，应先判断该用户是否收藏过该条新闻
        if news not in user.collection_news:
            user.collection_news.append(news)
    else:
        # 当取消收藏时，如果该新闻在该用户收藏列表中，才去删除
        if news in user.collection_news:
            user.collection_news.remove(news)

    return jsonify(errno=RET.OK, errmsg="OK")


@news_blu.route("/<int:news_id>")
@user_login
def detail(news_id):
    """
    新闻详情页面
    :param news_id:
    :return:
    """
    user = g.user

    # 1.显示新闻的点击排行
    clicks_news = []
    try:
        clicks_news = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)
    clicks_news_li = [news.to_basic_dict() for news in clicks_news]

    # 2.显示新闻的具体信息
    # 判断新闻id是否存在
    if not news_id:
        abort(404)
    # 判断新闻id类型是否是整型
    try:
        news_id = int(news_id)
    except Exception as e:
        current_app.logger.error(e)
        abort(404)
    # 通过新闻id查询新闻
    news = None
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
    # 判断新闻是否存在
    if not news:
        abort(404)

    news.clicks += 1
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)

    # 新闻详情页面收藏和已收藏  is_collected 进行标记
    is_collected = False
    # 用户已收藏的话把is_collected设置为True
    # 设置为True的条件：1.用户存在（已登录），2.新闻存在，3.该条新闻在用户收藏新闻的列表中
    if user and news in user.collection_news.all():
        is_collected = True

    data = {
        "user_info":user.to_dict() if user else None,
        "clicks_news_li":clicks_news_li,
        "news":news.to_dict(),
        "is_collected":is_collected
    }
    return render_template("news/detail.html", data=data)