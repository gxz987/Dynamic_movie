from flask import render_template, session, current_app, g, abort

from info import constants, db
from info.utils.common import user_login
from info.modules.news import news_blu
from info.models import News


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

    data = {
        "user_info":user.to_dict() if user else None,
        "clicks_news_li":clicks_news_li,
        "news":news.to_dict()
    }
    return render_template("news/detail.html", data=data)