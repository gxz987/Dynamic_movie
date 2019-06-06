from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_wtf import CSRFProtect
from flask_session import Session
from flask_script import Manager
from flask_migrate import MigrateCommand, Migrate

class Config(object):
    SECRET_KEY = '12314326'
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@127.0.0.1:3306/news'
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379

    # 设置session的保存方式
    SESSION_TYPE = 'redis'
    # 指定session的储存对象
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    # 是否加密
    SESSION_USE_SIGNER = True
    # 设置是否永久保存
    SESSION_PERMANENT = False
    # 设置session的过期时间
    PERMANENT_SESSION_LIFETIME = 86400 * 2


app = Flask(__name__)
# 1.集成配置类
app.config.from_object(Config)
# 2.集成SQLAlchemy
db = SQLAlchemy(app)
# 3.集成redis
redis_store = StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)
# 4.集成CSRFProtect
CSRFProtect(app)
# 5.集成flask_session, Session 指定session的保存路径
Session(app)
# 6.集成flask_script
manager = Manager(app)
# 7.集成flask_migrate， 在flask中对数据库进行迁移
Migrate(app, db)
manager.add_command("db", MigrateCommand)



@app.route('/')
def index():
    session["name"] = "hehehe"
    return 'ok'


if __name__ == '__main__':
    manager.run()
