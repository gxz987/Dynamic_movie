from redis import StrictRedis


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
