# from flask import logging
from redis import Redis
import logging



class Config(object):
    """工程配置信息"""

    SECRET_KEY ='qBcL8Eo43HhIa1i0yv0OdkUlr0L/aKGFl488chcqLN/1uXzKqNGzxnHpvS3MvBpb'

    # 数据库配置
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@127.0.0.1:3306/informations'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True  # 设置数据自动提交到数据库中：db.session.commit()
    # SQLALCHEMY_ECHO = True  # 后台打印数据查询时的SQL语句

    # Redis配置
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379

    # Session保存配置
    SESSION_TYPE = 'redis'  # 设置session保存到redis中
    SESSION_USE_SINGER = True  # 设置cookie中的session_id被加密签名处理
    SESSION_REDIS = Redis(host=REDIS_HOST, port=REDIS_PORT)  # 使用redis实例
    PERMANENT_SESSION_LIFETIME = 3600 * 24 * 2  # 设置session的过期时间，单位是秒

    # 默认日志等级
    LOG_LEVEL = logging.DEBUG


class DevelopmentConfig(Config):
    """开发环境下的配置"""
    DEBUG = True


class ProductionConfig(Config):
    """生产环境下的配置"""
    DEBUT = False
    LOG_LEVEL = logging.ERROR


class TestingConfig(Config):
    """单元测试环境下的配置"""
    DEBUT = True
    TESTING = True


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig
}