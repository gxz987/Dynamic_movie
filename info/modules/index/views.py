from flask import render_template, redirect, current_app, send_file, session
from info.modules.index import index_blu
from info.models import User, News

@index_blu.route('/')
def index():
    # 首页右上角的实现
    # 进入首页，需要判断用户是否登录，若已登录，将用户信息显示
    user_id = session.get("user_id")

    user = None
    if user_id:
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)

    # 1.显示新闻的点击排行
    clicks_news = []
    try:
        clicks_news = News.query.order_by(News.clicks.desc()).limit(6) # [news1, news2,...]
    except Exception as e:
        print("*" * 50)
        current_app.logger.error(e)

    clicks_news_li = [news.to_basic_dict() for news in clicks_news]

    # data = {"user_info":{"nick_name":"guo"}}
    data = {
        "user_info":user.to_dict() if user else None,
        "clicks_news_li":clicks_news_li
    }
    print(clicks_news)
    print(clicks_news_li)
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
