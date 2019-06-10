from flask import render_template, session, current_app, g

from info.utils.common import user_login
from info.modules.news import news_blu



@news_blu.route("/<int:news_id>")
@user_login
def detail(news_id):
    """
    新闻详情页面
    :param news_id:
    :return:
    """
    user = g.user

    data = {
        "user_info":user.to_dict() if user else None
    }
    return render_template("news/detail.html", data=data)