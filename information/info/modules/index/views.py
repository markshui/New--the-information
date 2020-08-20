from flask import render_template, current_app, session, request, jsonify, g
from info import redis_store, constants
from info.models import User, News, Category
from info.utils.common import user_login_data
from info.utils.response_code import RET
from . import index_blue


@index_blue.route('/news_list')
def news_list():
    """
    获取指定分类的新闻列表
    :return:
    """

    # 1、获取参数
    cid = request.args.get('cid', '1')  # 新闻分类id
    page = request.args.get('page', '1')  # 当前页码数
    per_page = request.args.get('per_page', '10')  # 每页显示多少条新闻

    # 2、校验参数
    try:
        cid = int(cid)
        page = int(page)
        per_page = int(per_page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')

    # 3、查询数据并分页
    filters = [News.status == 0]
    if cid != 1:
        filters.append(News.category_id == cid)

    try:
        paginate = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page, per_page, False)
        current_page = paginate.page  # 当前页码数
        total_page = paginate.pages  # 总页码数
        items = paginate.items  # 返回的是新闻模型数据对象，需要转换为字典
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据查询错误')

    news_li = []
    for news in items:
        news_li.append(news.to_basic_dict())

    data = {
        "cid": cid,
        "current_page": current_page,
        "total_page": total_page,
        "news_li": news_li
    }

    # 4、返回数据
    return jsonify(errno=RET.OK, errmsg='OK', data=data)


@index_blue.route('/')
@user_login_data
def index():

    # 右侧新闻排行的逻辑
    news_list = []
    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)

    # 定义一个用来存储字典的空列表
    click_news_list = []
    for news in news_list:
        click_news_list.append(news.to_basic_dict())

    # 获取新闻分类数据
    categories = Category.query.all()
    category_li = []
    for category in categories:
        category_li.append(category.to_dict())

    data = {
        "user": g.user.to_dict() if g.user else None,
        "click_news_list": click_news_list,
        "category_li": category_li
    }

    return render_template('news/index.html', data=data)


# 自定义视图函数，访问网站图标
# send_static_file是系统访问静态文件所调用的方法
@index_blue.route('/favicon.ico')
def favicon():
    return current_app.send_static_file('news/favicon.ico')