import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, g, render_template
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_wtf.csrf import generate_csrf
from redis import Redis
from config import config




# 初始化数据库
# 在flask扩展中，很多可以先初始化扩展的对象，然后再去调用init_app方法初始化

db = SQLAlchemy()

redis_store = None  # type: Redis


def setup_log(config_name):
    """配置日志",并传入配置名字，以便能获取到指定配置所对应的日志等级"""

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


def create_app(config_name):
    """通过传入不同的配置名字，初始化其对应配置的应用实例"""

    # 配置项目日志
    setup_log(config_name)

    app = Flask(__name__)
    # 加载配置
    app.config.from_object(config[config_name])

    # 通过app初始化
    db.init_app(app)

    # 初始化redis存储对象
    global redis_store
    redis_store = Redis(
        host=config[config_name].REDIS_HOST,
        port=config[config_name].REDIS_PORT,
        decode_responses=True
    )

    # 开启CSRF保护，用于服务器验证功能
    CSRFProtect(app)

    """
    csrf_token校验原理，操作步骤如下：
    1、后端生成csrf_token的值，在前端请求登录或注册界面时将值传给前端，传给前端的方式有两种：
        (1)在模板中Form表单中添加隐藏字段
        (2)将csrf_token使用cookie的方式传给前端
    2、在前端发起请求时，在表单或请求头中带上指定的csrf_token。
    3、后端在接受请求之后，获取到前端发送过来的csrf_token，与第1步生成的csrf_token的值进行校验
    4、如果校验csrf_token一致，则代表是正常的请求，否则可能是伪造请求，不予通过。
    
    在Flask中，CSRFProtect这个类专门只对指定app进行csrf_token校验操作，所以开发者需要做以下几件事情：
    1、生成csrf_token的值
    2、将csrf_token的值传给前端浏览器
    3、在前端请求时带上csrf_token值
    """

    @app.after_request
    def after_request(response):
        csrf_token = generate_csrf()
        response.set_cookie('csrf_token', csrf_token)
        return response

    # 注册自定义过滤器
    from info.utils.common import do_index_class
    app.add_template_filter(do_index_class, 'index_class')

    # 设置session保存指定位置
    Session(app)

    # 注册首页模块蓝图
    from info.modules.index import index_blue
    app.register_blueprint(index_blue)
    # 注册用户中心蓝图
    from info.modules.passport import passport_blue
    app.register_blueprint(passport_blue)
    # 注册新闻模块蓝图
    from info.modules.news import news_blue
    app.register_blueprint(news_blue)
    # 注册用户中心模块蓝图
    from info.modules.profile import profile_blue
    app.register_blueprint(profile_blue)
    #　注册后台管理模块蓝图
    from info.modules.admin import admin_blue
    app.register_blueprint(admin_blue)


    from info.utils.common import user_login_data
    @app.errorhandler(404)
    @user_login_data
    def page_not_found(error):
        """404页面逻辑"""

        user = g.user
        data = {
            "user": user.to_dict() if user else None
        }
        return render_template("news/404.html", data=data)

    return app
