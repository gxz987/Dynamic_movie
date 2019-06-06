from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_wtf import CSRFProtect
from flask_session import Session

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
