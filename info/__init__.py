from flask import Flask
from config import config
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_wtf import CSRFProtect
from flask_session import Session


# 只要是可变的参数：一、可以放在配置文件中，二、用函数封装 三、用全局变量
# 所有可变的参数用函数的形参来代替
def create_app(config_name):
    app = Flask(__name__)
    # 1.集成配置类
    app.config.from_object(config[config_name])
    # 2.集成SQLAlchemy
    db = SQLAlchemy(app)

    # 3.集成redis
    redis_store = StrictRedis(host=config[config_name].REDIS_HOST, port=config[config_name].REDIS_PORT)
    # 4.集成CSRFProtect
    CSRFProtect(app)
    # 5.集成flask_session, Session 指定session的保存路径
    Session(app)
    return app
