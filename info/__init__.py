import logging
from logging.handlers import RotatingFileHandler

from flask import Flask, render_template, g

from info.utils.common import user_login
from config import config
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_wtf.csrf import CSRFProtect, generate_csrf
from flask_session import Session


# db = SQLAlchemy(app)  # 拆分成两步
# db = SQLAlchemy()
# db.init_app(app)


db = SQLAlchemy()

def setup_log(config_name):
    """配置日志:通过不同的配置创建出不同是日志记录"""
    # 设置日志的记录等级
    logging.basicConfig(level=config[config_name].LOG_LEVEL)  # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)


redis_store = None  # type:StrictRedis

# 只要是可变的参数：一、可以放在配置文件中，二、用函数封装 三、用全局变量
# 所有可变的参数用函数的形参来代替
def create_app(config_name):
    setup_log(config_name)
    app = Flask(__name__)
    # 1.集成配置类
    app.config.from_object(config[config_name])
    # 2.集成SQLAlchemy
    # db = SQLAlchemy(app)
    db.init_app(app)
    # 3.集成redis
    global redis_store
    redis_store = StrictRedis(host=config[config_name].REDIS_HOST, port=config[config_name].REDIS_PORT,
                              decode_responses=True)
    # 4.集成CSRFProtect
    # 1.先向cookie中添加一个csrf_token
    @app.after_request
    def after_request(response):
        csrf_token = generate_csrf()
        response.set_cookie("csrf_token", csrf_token)
        return response


    @app.errorhandler(404)
    @user_login
    def get_404_error(e):
        """
        捕获404错误
        :return:
        """
        # user = g.user
        # if user:
        #     data = {
        #         "user_info":user.to_dict()
        #     }
        # else:
        #     data = {}
        data = {
            "user_info":g.user.to_dict() if g.user else None
        }

        return render_template("news/404.html", data=data)


    CSRFProtect(app)   # INFO:flask_wtf.csrf:The CSRF token is missing.
    # 5.集成flask_session, Session 指定session的保存路径
    Session(app)

    # 注册过滤器
    from info.utils.common import do_index_class
    app.add_template_filter(do_index_class, "indexClass")


    # 注册蓝图
    # 蓝图模块在哪使用就在哪导入，解决循环导入问题
    from info.modules.index import index_blu
    app.register_blueprint(index_blu)
    from info.modules.passport import passport_blu
    app.register_blueprint(passport_blu)
    from info.modules.news import news_blu
    app.register_blueprint(news_blu)
    from info.modules.profile import profile_blu
    app.register_blueprint(profile_blu)
    from info.modules.admin import admin_blu
    app.register_blueprint(admin_blu)

    return app
