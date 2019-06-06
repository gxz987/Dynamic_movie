import logging
from logging.handlers import RotatingFileHandler

from flask import Flask
from config import config
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_wtf import CSRFProtect
from flask_session import Session
from info.modules.index import index_blu


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
    redis_store = StrictRedis(host=config[config_name].REDIS_HOST, port=config[config_name].REDIS_PORT)
    # 4.集成CSRFProtect
    CSRFProtect(app)
    # 5.集成flask_session, Session 指定session的保存路径
    Session(app)

    # 注册蓝图
    app.register_blueprint(index_blu)

    return app
