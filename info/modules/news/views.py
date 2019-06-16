from flask import render_template, session, current_app, g, abort, jsonify, request

from info import constants, db
from info.utils.common import user_login
from info.modules.news import news_blu
from info.models import News, User, Comment, CommentLike
from info.utils.response_code import RET


@news_blu.route("/followed_user", methods=["POST"])
@user_login
def followed_user():
    """关注和取消关注用户"""
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")

    # 获取参数
    user_id = request.json.get("user_id")
    action = request.json.get("action")

    if not all([user_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    if action not in ["follow", "unfollow"]:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 取到要被关注的用户
    try:
        author = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询错误")
    if not author:
        return jsonify(errno=RET.NODATA, errmsg="未查询到数据")

    # 根据要执行的操作去修改对应的数据
    if action == "follow":
        # 关注用户
        if user not in author.followers:
            author.followers.append(user)
        else:
            return jsonify(errno=RET.DATAEXIST, errmsg="当前用户已被关注")
    else:
        # 取消关注
        if user in author.followers:
            author.followers.remove(user)
        else:
            return jsonify(errno=RET.DATAEXIST, errmsg="当前用户未被关注")

    return jsonify(errno=RET.OK, errmsg="操作成功")


@news_blu.route("/comment_like", methods=["POST"])
@user_login
def set_comment_like():
    """
    评论的点赞和取消点赞功能
    1.接收参数： comment_id  action(add,remove其中之一)
    2.参数校验
    3.CommentLike()点赞表中添加或删除一条数据；业务逻辑
    4.返回响应
    :return:
    """
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")

    comment_id = request.json.get("comment_id")
    action = request.json.get("action")

    if not all([]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    try:
        comment_id = int(comment_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    if action not in ["add", "remove"]:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    try:
        comment = Comment.query.get(comment_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询错误")
    if not comment:
        return jsonify(errno=RET.NODATA, errmsg="新闻不存在")

    # 业务逻辑
    comment_like_obj = CommentLike.query.filter(CommentLike.comment_id==comment_id, CommentLike.user_id==user.id).first()

    if action == "add":
        if not comment_like_obj:
            # 初始化一个点赞对象
            comment_like = CommentLike()
            comment_like.comment_id = comment_id
            comment_like.user_id = user.id
            db.session.add(comment_like)
            comment.like_count += 1
    else:
        if comment_like_obj:
            db.session.delete(comment_like_obj)
            comment.like_count -= 1

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库保存失败")

    return jsonify(errno=RET.OK, errmsg="OK")


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
    if parent_id:
        comment.parent_id = parent_id
    try:
        db.session.add(comment)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
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

    # 3.新闻详情页面收藏和已收藏  is_collected 进行标记
    is_collected = False
    # 用户已收藏的话把is_collected设置为True
    # 设置为True的条件：1.用户存在（已登录），2.新闻存在，3.该条新闻在用户收藏新闻的列表中
    if user and news in user.collection_news.all():
        is_collected = True

    # 用户关注作者
    is_followed = False
    author = news.user
    if user and author:
        # 如果user在作者的粉丝中
        if user in author.followers:
            is_followed = True
            # # 如果作者这用户的
            # if author in user.followed:
            #     is_followed = True

    # 4.查询当前新闻下的所有的评论，按时间降序排列
    comments = []
    try:
        comments = Comment.query.filter(Comment.news_id == news_id).order_by(Comment.create_time.desc()).all()
    except Exception as e:
        current_app.logger.error(e)

    # comments_dict_li = [comment.to_dict() for comment in comments]
    comments_dict_li = []
    for comment in comments:
        comment_dict = comment.to_dict()
        comment_dict["is_like"] = False
        # 如果comment_dict["is_like"] = True 代表已经点赞
        # 如果该用户存在，并且通过该用户和该条评论查询点赞，如果有值 True
        if user and CommentLike.query.filter(CommentLike.comment_id == comment.id, CommentLike.user_id == user.id).first():
            comment_dict["is_like"] = True
        comments_dict_li.append(comment_dict)

    data = {
        "user_info":user.to_dict() if user else None,
        "clicks_news_li":clicks_news_li,
        "news":news.to_dict(),
        "is_collected":is_collected,
        "comments_dict_li": comments_dict_li,
        "is_followed": is_followed
    }

    return render_template("news/detail.html", data=data)