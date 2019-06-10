from flask import render_template, session, current_app, g

import constants
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


    data = {
        "user_info":user.to_dict() if user else None,
        "clicks_news_li":clicks_news_li
    }
    return render_template("news/detail.html", data=data)