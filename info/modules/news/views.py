from flask import render_template, session, current_app

from info.modules.news import news_blu



@news_blu.route("/<int:news_id>")
def detail(news_id):
    """
    新闻详情页面
    :param news_id:
    :return:
    """
    user_id = session.get("user_id")
    user = None
    if user_id:
        try:
            from info.models import User
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)

    data = {
        "user_info":user.to_dict() if user else None
    }
    return render_template("news/detail.html", data=data)