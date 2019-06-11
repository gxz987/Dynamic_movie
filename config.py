from redis import StrictRedis
import logging

class Config(object):
    SECRET_KEY = '12314326'
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
    # 设置存活时间,若为false，cookie的存活时间为浏览器回话结束；
    # 若为True，cookie的过期时间和session一样
    SESSION_PERMANENT = False
    # 设置session的过期时间
    PERMANENT_SESSION_LIFETIME = 86400 * 2

    # 设置数据库的默认提交
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

class DevelopConfig(Config):
    """开发模式"""
    DEBUG = True
    LOG_LEVEL = logging.DEBUG


class ProductConfig(Config):
    """生产模式"""
    LOG_LEVEL = logging.ERROR


class TestingConfig(Config):
    """调试模式"""
    DEBUG = True


# 使用字典封装
config = {
    "develop": DevelopConfig,
    "product": ProductConfig,
    "testing": TestingConfig
}
