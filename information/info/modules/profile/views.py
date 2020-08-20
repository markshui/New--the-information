from flask import g, redirect, render_template, request, jsonify, current_app, session, abort

from info import db, constants
from info.models import Category, News, User
from info.modules.profile import profile_blue
from info.utils.common import user_login_data
from info.utils.image_storage import storage
from info.utils.response_code import RET


@profile_blue.route('/other_news_list')
@user_login_data
def other_news_list():
    """其它用户新闻列表"""

    page = request.args.get("page", 1)
    user_id = request.args.get("user_id")

    try:
        page = int(page)
    except Exception as e:
        current_app.logger.erroe(e)
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')

    if not all([page, user_id]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')

    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据查询错误')

    if not user:
        return jsonify(errno=RET.NODATA, errmsg='用户不存在')

    try:
        paginate = News.query.filter_by(user_id=user.id).paginate(page, 1, False)
        news_li = paginate.items
        current_page = paginate.page
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据查询错误')

    news_dict_li = []
    for news in news_li:
        news_dict_li.append(news.to_review_dict())

    data = {
        "news_list": news_dict_li,
        "current_page": current_page,
        "total_page": total_page
    }

    return jsonify(errno=RET.OK, errmsg='OK', data=data)


@profile_blue.route('/other_info')
@user_login_data
def other_info():
    """查看其它用户信息"""

    user = g.user

    # 获取其它用户id
    user_id = request.args.get('id')
    if not user_id:
        abort(404)

    # 查询用户模型
    other_user = None
    try:
        other_user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.erroe(e)

    if not other_user:
        abort(404)

    # 判断当前登录用户是否关注该用户
    is_followed = False
    if g.user:
        if other_user.followers.filter(User.id == user.id).count() > 0:
            is_followed = True

    data = {
        "user": user.to_dict() if user else None,
        "other_user": other_user.to_dict(),
        "is_followed": is_followed
    }

    return render_template('news/other.html', data=data)


@profile_blue.route('/user_follow')
@user_login_data
def user_follow():
    """我的关注"""

    page = request.args.get("page", 1)
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.erroe(e)
        page = 1

    user = g.user

    follows = []
    current_page = 1
    total_page = 1
    try:
        paginate = user.followed.paginate(page, constants.USER_FOLLOWED_MAX_COUNT, False)
        # paginate = user.followed.paginate(page, 1, False)
        follows = paginate.items
        current_page = paginate.page
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.erroe(e)

    user_dict_li = []
    for follow_user in follows:
        user_dict_li.append(follow_user.to_dict())

    data = {
        "users": user_dict_li,
        "current_page": current_page,
        "total_page": total_page
    }

    return render_template('news/user_follow.html', data=data)


@profile_blue.route('/news_list')
@user_login_data
def news_list():
    """用户发布的新闻列表"""

    page = request.args.get('page', 1)
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    user = g.user
    news_li = []
    current_page = 1
    total_page = 1
    try:
        # 查询分页数据
        paginate = News.query.filter_by(user_id=user.id).paginate(page, constants.USER_COLLECTION_MAX_NEWS, False)
        # 获取当前页数据
        news_li = paginate.items
        # 获取当前页
        current_page = paginate.page
        # 获取总页数
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.erroe(e)

    news_dict_li = []
    for news in news_li:
        news_dict_li.append(news.to_review_dict())

    data = {
        "current_page": current_page,
        "total_page": total_page,
        "news_list": news_dict_li
    }

    return render_template('news/user_news_list.html', data=data)


@profile_blue.route('/news_release', methods=['GET', 'POST'])
@user_login_data
def news_release():
    """新闻发布"""

    if request.method == 'GET':

        categories = []
        try:
            # 获取所有的分类数据
            categories = Category.query.all()
        except Exception as e:
            current_app.logger.error(e)

        # 定义列表保存分类数据
        categories_list = []
        for category in categories:
            categories_list.append(category.to_dict())

        # 移除 最新 分类
        categories_list.pop(0)

        data = {
            "categories": categories_list
        }

        return render_template('news/user_news_release.html', data=data)

    # POST提交，执行新闻发布操作

    # 1.获取提交的数据
    title = request.form.get('title')  # 新闻标题
    source = "个人发布"
    category_id = request.form.get('category_id')  # 分类ID
    digest = request.form.get('digest')  # 新闻摘要
    index_image = request.files.get('index_image')  # 索引图片
    content = request.form.get('content')  # 新闻内容

    if not all([title, source, category_id, digest, index_image, content]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数有误')

    # 读取图片
    try:
        index_image = index_image.read()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='参数有误')

    # 将新闻图片上传到七牛
    try:
        url = storage(index_image)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg='上传图片错误')

    # 初始化新闻模型，并设置相关数据
    news = News()
    news.title = title
    news.source = source
    news.category_id = category_id
    news.digest = digest
    news.index_image_url = constants.QINIU_DOMIN_PREFIX + url
    news.content = content
    news.user_id = g.user.id
    news.status = 1  # 待审核状态

    # 数据自动提交
    db.session.add(news)

    # 返回结果
    return jsonify(errno=RET.OK, errmsg='发布成功，等待审核！')


@profile_blue.route('/collection')
@user_login_data
def user_collection():
    """用户收藏"""

    page = request.args.get("page", 1)  # 默认返回第1页
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    user = g.user
    collections = []
    current_page = 1
    total_page = 1

    try:
        # 分页数据查询
        paginate = user.collection_news.paginate(page, constants.USER_COLLECTION_MAX_NEWS, False)
        # 获取分页数据
        collections = paginate.items
        # 获取当前页
        current_page = paginate.page
        # 获取总页数
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)

    # 收藏列表
    collection_list = []
    for news in collections:
        collection_list.append(news.to_basic_dict())

    data = {
        "total_page": total_page,
        "current_page": current_page,
        "collections": collection_list
    }

    return render_template('news/user_collection.html', data=data)


@profile_blue.route('/pwd_info', methods=['GET', 'POST'])
@user_login_data
def pwd_info():
    if request.method == 'GET':
        return render_template('news/user_pwd_info.html')

    # 1.获取参数
    old_pwd = request.json.get('old_password')
    new_pwd = request.json.get('new_password')

    if not all([old_pwd, new_pwd]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数有误')

    # 2.获取当前登录用户的信息
    user = g.user
    # 校验用户输入的原密码
    if not user.check_passowrd(old_pwd):
        return jsonify(errno=RET.PWDERR, errmsg="原密码错误")

    # 更新密码
    user.password = new_pwd
    # 自动提交数据

    return jsonify(errno=RET.OK, errmsg='保存成功')


@profile_blue.route('/pic_info', methods=['GET', 'POST'])
@user_login_data
def pic_info():
    """上传图像"""
    user = g.user
    if request.method == "GET":
        return render_template('news/user_pic_info.html', data={"user": user.to_dict()})

    # 1.获取上传的文件
    try:
        avatar_file = request.files.get('avatar').read()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='读取文件出错')

    # 2.将文件上传到七牛云
    try:
        url = storage(avatar_file)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg='上传图片错误')

    # 3.将头像信息更新到当前用户的模型中

    # 设置用户模型相关数据
    user.avatar_url = url
    # 将数据保存到数据库中
    # try:
    #     db.session.commit()
    # except Exception as e:
    #     current_app.logger.error(e)
    #     db.session.rollback()
    #     return jsonify(errno=RET.DBERR, errmsg="保存用户数据错误")

    # 返回上传的结果(avatar_url)
    return jsonify(errno=RET.OK, errmsg="OK", data={"avatar_url": constants.QINIU_DOMIN_PREFIX + url})


@profile_blue.route('/base_info', methods=['GET', 'POST'])
@user_login_data
def base_info():
    """
    用户基本信息
    1.获取用户登录信息
    2.获取提交的数据
    3.更新并保存数据库中
    4.返回结果
    :return:
    """

    # 1.获取当前登录的用户的信息
    user = g.user
    if request.method == "GET":
        return render_template('news/user_base_info.html',  data={"user": user.to_dict()})

    # 获取传入的参数
    nick_name = request.json.get("nick_name")
    signature = request.json.get("signature")
    gender = request.json.get("gender")
    if not all([nick_name, signature, gender]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数有误")

    if gender not in ["MAN", "WOMEN"]:
        return jsonify(errno=RET.PARAMERR, errmsg="参数有误")

    # 3.更新并保存数据
    user.nick_name = nick_name
    user.signature = signature
    user.gender = gender
    # 项目配置文件中已配置了数据自动提交
    # try:
    #     db.session.commit()
    # except Exception as e:
    #     current_app.logger.error(e)
    #     db.session.rollback()
    #     return jsonify(errno=RET.DBERR, errmsg="保存数据失败")

    # 将session中保存的数据进行实时更新
    session['nick_name'] = nick_name

    # 4.返回响应
    return jsonify(errno=RET.OK, errmsg='更新成功')


@profile_blue.route('/info')
@user_login_data
def user_info():
    """
    获取用户信息
    """

    user = g.user
    if not user:
        # 如果用户未登录，则重定向到首页
        return redirect('/')

    data = {
        "user": user.to_dict()
    }
    return render_template("news/user.html", data=data)