import time
from datetime import datetime, timedelta

from flask import render_template, request, current_app, session, g, redirect, url_for, jsonify

from info import constants, db
from info.models import User, News, Category
from info.modules.admin import admin_blue
from info.utils.common import user_login_data
from info.utils.image_storage import storage
from info.utils.response_code import RET


@admin_blue.route('/add_type', methods=['POST'])
def add_category():
    """新增新闻分类"""

    category_id = request.json.get('id')
    category_name = request.json.get('name')
    if not category_name:
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')

    # 判断是否有分类id
    if category_id:
        # 如果有分类id，代表是修改分类的操作
        try:
            category = Category.query.get(category_id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg='数据查询失败')

        if not category:
            return jsonify(errno=RET.NODATA, errmsg='未查询到该分类信息')
        # 更新分类名称
        category.name = category_name
    else:
        # 新增分类
        category = Category()
        category.name = category_name
        db.session.add(category)

    return jsonify(errno=RET.OK, errmsg='保存数据成功')


@admin_blue.route('/news_type')
def news_category():
    """新闻分类列表"""

    # 获取所有的分类数据
    categories = Category.query.all()

    categories_li = []
    for category in categories:
        categories_li.append(category.to_dict())

    # 移除 最新 分类
    categories_li.pop(0)

    return render_template('admin/news_type.html', data={'categories': categories_li})


@admin_blue.route('/news_edit_detail', methods=['GET', 'POST'])
def news_edit_detail():
    """新闻编辑详情"""

    if request.method == 'GET':
        news_id = request.args.get('news_id')
        if not news_id:
            return render_template('admin/news_edit_detail.html', data={'errmsg': '未查询到此新闻'})

        # 查询新闻
        news = None
        try:
            news = News.query.get(news_id)
        except Exception as e:
            current_app.logger.error(e)

        if not news:
            return render_template('admin/news_edit_detail.html', data={'errmsg': '未查询到此新闻'})

        # 查询分类数据
        categories = Category.query.all()
        categories_li = []
        for category in categories:
            cate_dict = category.to_dict()
            cate_dict['is_selected'] = False
            if category.id == news.category_id:
                cate_dict['is_selected'] = True
            categories_li.append(cate_dict)

        # 移除 最新 分类
        categories_li.pop(0)

        data = {
            'news': news.to_dict(),
            "categories": categories_li
        }

        return render_template('admin/news_edit_detail.html', data=data)

    # 执行新闻编辑后提交操作

    news_id = request.form.get('news_id')
    title = request.form.get('title')
    digest = request.form.get('digest')
    content = request.form.get('content')
    index_image = request.files.get('index_image')
    category_id = request.form.get('category_id')

    if not all([title, digest, content, category_id]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')

    news = None
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)

    if not news:
        return jsonify(errno=RET.NODATA, errmsg='未查询到此新闻')

    if index_image:
        try:
            index_image = index_image.read()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.PARAMERR, errmsg='参数有误')

        # 将图片上传到七牛
        try:
            url = storage(index_image)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.THIRDERR, errmsg='上传图片失败')

        # 更新新闻的url
        news.index_image_url = constants.QINIU_DOMIN_PREFIX + url

    # 更新新闻的相关数据
    news.title = title
    news.digest = digest
    news.content = content
    news.category_id = category_id

    return jsonify(errno=RET.OK, errmsg='编辑成功')


@admin_blue.route('/news_edit')
def news_edit():
    """新闻编辑列表"""

    page = request.args.get('page', 1)
    keywords = request.args.get('keywords', '')

    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    news_list = []
    current_page = 1
    total_page = 1

    try:
        filters = []
        if keywords:
            # 添加关键词的检索选项
            filters.append(News.title.contains(keywords))

        # 查询分页数据
        paginate = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page, constants.ADMIN_NEWS_PAGE_MAX_COUNT, False)

        news_list = paginate.items
        current_page = paginate.page
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)

    news_dict_list = []
    for news in news_list:
        news_dict_list.append(news.to_basic_dict())
    data = {
        "total_page": total_page,
        "current_page": current_page,
        "news_list": news_dict_list
    }

    return render_template('admin/news_edit.html', data=data)


@admin_blue.route('/news_review_action', methods=['GET', 'POST'])
def news_review_detail():
    """新闻审核"""

    if request.method == 'GET':
        # 获取新闻id
        news_id = request.args.get('news_id')
        if not news_id:
            return render_template('admin/news_review_detail.html', data={"errmsg": "参数错误"})

        news = None
        try:
            news = News.query.get(news_id)
        except Exception as e:
            current_app.logger.error(e)

        if not news:
            return render_template('admin/news_review_detail.html', data={"errmsg": "未查询到此新闻"})

        # 返回数据
        data = {
            "news": news.to_dict()
        }

        return render_template('admin/news_review_detail.html', data=data)

    # 执行新闻审核操作
    # 获取参数
    news_id = request.json.get('news_id')
    action = request.json.get('action')

    if not all([news_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')
    if action not in ['accept', 'reject']:
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')

    news = None
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)

    if not news:
        return jsonify(errno=RET.DBERR, errmsg='未查询到数据')

    if action == 'accept':
        # 审核通过
        news.status = 0
    else:
        # 审核不通过
        reason = request.json.get('reason')
        if not reason:
            return jsonify(errno=RET.PARAMERR, errmsg='参数错误')
        news.reason = reason
        news.status = -1

    return jsonify(errno=RET.OK, errmsg='操作成功')


@admin_blue.route('/news_review')
def news_review():
    """待审核的新闻列表"""

    # 获取参数
    page = request.args.get('page', 1)
    keywords = request.args.get('keywords', '')

    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    news_list = []
    current_page = 1
    total_page = 1

    try:
        filters = [News.status != 0]

        # 判断用户是否通过关键词进行筛选
        if keywords:
            filters.append(News.title.contains(keywords))

        # 查询分页数据
        paginate = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page, 2, False)
        news_list = paginate.items
        current_page = paginate.page
        total_page = paginate.pages
    except Exception as e:
        current_page.logger.error(e)

    news_dict_list = []
    for news in news_list:
        news_dict_list.append(news.to_review_dict())

    data = {
        'total_page': total_page,
        'current_page': current_page,
        'news_list': news_dict_list
    }
    return render_template('admin/news_review.html', data=data)

@admin_blue.route('/user_list')
def user_list():
    """获取用户列表"""

    # 获取参数
    page = request.args.get('page', 1)
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    users = []
    current_page = 1
    total_page = 1

    # 查询数据
    try:
        paginate = User.query.filter_by(is_admin=False).order_by(User.last_login.desc()).paginate(page, constants.ADMIN_USER_PAGE_MAX_COUNT, False)
        users = paginate.items
        current_page = paginate.page
        total_page = paginate.pages
    except Exception as e:
        current_page.logger.error(e)

    # 将模型列表转化成字典列表
    users_li = []
    for user in users:
        # print(user.to_admin_dict())
        users_li.append(user.to_admin_dict())

    data = {
        "total_page": total_page,
        "current_page": current_page,
        'users': users_li
    }

    return render_template('admin/user_list.html',  data=data)


@admin_blue.route('/user_count')
def user_count():
    """用户统计"""

    now = time.localtime()

    # 查询用户总数
    total_count = 0
    try:
        total_count = User.query.filter_by(is_admin=False).count()
    except Exception as e:
        current_app.logger.error(e)

    # 查询月新增数
    mon_count = 0
    try:
        mon_begin_date = datetime.strptime('%d-%02d-01' % (now.tm_year, now.tm_mon), '%Y-%m-%d')
        mon_count = User.query.filter(User.is_admin == False, User.create_time >= mon_begin_date).count()
    except Exception  as e:
        current_app.logger.error(e)

    # 查询日新增数
    day_count = 0
    try:
        day_begin_date = datetime.strptime('%d-%02d-%02d' % (now.tm_year, now.tm_mon, now.tm_mday), '%Y-%m-%d')
        day_count = User.query.filter(User.is_admin == False, User.create_time >= day_begin_date).count()
    except Exception  as e:
        current_app.logger.error(e)

    # 拆线图数据
    active_time = []
    active_count = []

    # 获取当前的时间字符串
    today_date_str = '%d-%02d-%02d' % (now.tm_year, now.tm_mon, now.tm_mday)

    # 将当前的时间字符串转化成时间对象
    today_date = datetime.strptime(today_date_str, '%Y-%m-%d')

    for i in range(0, 31):
        # 获取某天的0点0分
        begin_date = today_date - timedelta(days=i)
        # 获取下一天的0点0分
        end_date = today_date - timedelta(days=i-1)

        count = User.query.filter(User.is_admin == False, User.last_login >= begin_date, User.last_login <= end_date).count()
        active_count.append(count)
        active_time.append(begin_date.strftime('%Y-%m-%d'))

    active_time.reverse()
    active_count.reverse()

    data = {
        "total_count": total_count,
        "mon_count": mon_count,
        "day_count": day_count,
        "active_time": active_time,
        "active_count": active_count
    }

    return render_template('admin/user_count.html', data=data)


@admin_blue.route('/index')
@user_login_data
def admin_index():
    """后台管理首页"""

    user = g.user
    return render_template('admin/index.html', user=user.to_dict())


@admin_blue.route('/login', methods=['GET', 'POST'])
def admin_login():
    """管理用户登录"""

    if request.method == 'GET':
        user_id = session.get('user_id', None)
        is_admin = session.get('is_admin', False)
        # 如果当前登录用户是管理员帐号，则直接跳转到后台首页
        if user_id and is_admin:
            return redirect(url_for('admin.admin_index'))
        return render_template("admin/login.html")

    # 获取登录参数
    username = request.form.get("username")
    password = request.form.get("password")
    if not all([username, password]):
        return render_template("admin/login.html", errmsg='用户或密码不正确')

    try:
        user = User.query.filter_by(mobile=username).first()
    except Exception as e:
        current_app.logger.erroe(e)
        return render_template('admin/login.html', errmsg="数据查询错误")

    if not user:
        return render_template("admin/login.html", errmsg='用户不存在')

    if not user.check_passowrd(password):
        return render_template("admin/login.html", errmsg='用户或密码不正确', username=username)

    if not user.is_admin:
        return render_template('admin/login.html', errmsg='用户权限错误')

    session['user_id'] = user.id
    session['nick_name'] = user.nick_name
    session['mobile'] = user.mobile
    session['is_admin'] = True

    # 跳转到后台管理首页
    return redirect(url_for('admin.admin_index'))
