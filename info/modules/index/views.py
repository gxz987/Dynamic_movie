from flask import render_template, redirect, current_app, send_file
from info.modules.index import index_blu


@index_blu.route('/')
def index():
    return render_template("news/index.html")


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
