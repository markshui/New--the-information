from flask import render_template, g, current_app, abort, request, jsonify, session

from info import constants, db
from info.models import News, Comment, CommentLike, User
from info.modules.news import news_blue
from info.utils.common import user_login_data
from info.utils.response_code import RET


# /news/followed_user
@news_blue.route('/followed_user', methods=['POST'])
@user_login_data
def followed_user():
    """关注/取消关注用户"""

    if not g.user:
        return jsonify(errno=RET.SESSIONERR, errmsg='用户未登录')

    user_id = request.json.get('user_id')
    action = request.json.get('action')

    if not all([user_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')

    if action not in ['follow', 'unfollow']:
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')

    # 查询到关注的用户信息
    try:
        target_user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询数据失败')

    if not target_user:
        return jsonify(errno=RET.NODATA, errmsg='未查询到相关数据')

    # 根据不同操作做不同逻辑
    if action == "follow":
        # 关注该用户
        if target_user.followers.filter(User.id == g.user.id).count() > 0:
            return jsonify(errno=RET.DATAEXIST, errmsg='已关注该用户')
        else:
            target_user.followers.append(g.user)
    else:
        # 取消关注该用户
        if target_user.followers.filter(User.id == g.user.id).count() > 0:
            target_user.followers.remove(g.user)

    # 自动提交数据

    return jsonify(errno=RET.OK, errmsg='操作成功')


@news_blue.route('/comment_like', methods=['POST'])
@user_login_data
def comment_like():
    """评论点赞"""

    if not g.user:
        return jsonify(errno=RET.SESSIONERR, errmsg='用户未登录')

    # 获取参数
    comment_id = request.json.get('comment_id')
    action = request.json.get('action')

    # 判断参数
    if not all([comment_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')

    if action not in ['add', 'remove']:
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')


    try:
        comment_id = int(comment_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')

    # 查询数据
    try:
        comment = Comment.query.get(comment_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询数据失败')

    if not comment:
        return jsonify(errno=RET.NODATA, errmsg='评论数据不存在')

    if action  == 'add':
        # 点赞评论
        comment_like_obj = CommentLike.query.filter_by(comment_id=comment_id, user_id=g.user.id).first()
        if not comment_like_obj:
            comment_like_obj = CommentLike()
            comment_like_obj.comment_id = comment_id
            comment_like_obj.user_id = g.user.id
            db.session.add(comment_like_obj)
            # 增加点赞个数
            comment.like_count += 1
    else:
        # 取消点赞
        comment_like_obj = CommentLike.query.filter_by(comment_id=comment_id, user_id=g.user.id).first()
        if comment_like_obj:
            db.session.delete(comment_like_obj)
            comment.like_count -= 1

    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='操作失败')

    return jsonify(errno=RET.OK, errmsg='操作成功')


@news_blue.route('/news_comment', methods=['post'])
@user_login_data
def news_comment():
    """评论新闻和回复评论"""

    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg='用户未登录')

    # 获取参数
    news_id = request.json.get('news_id')
    comment_content = request.json.get('comment')
    parent_id = request.json.get('parent_id')

    if not all([news_id, comment_content]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不足')

    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询数据失败')

    if not news:
        return jsonify(errno=RET.NODATA, errmsg='该新闻不存在')

    # 初始化模型
    comment_obj = Comment()
    comment_obj.user_id = user.id
    comment_obj.news_id = news_id
    comment_obj.content = comment_content
    if parent_id:
        comment_obj.parent_id = parent_id

    #　保存数据到数据库
    try:
        db.session.add(comment_obj)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='保存评论数据失败')

    return jsonify(errno=RET.OK, errmsg='评论成功', data=comment_obj.to_dict())


@news_blue.route('/news_collect', methods=['post'])
@user_login_data
def news_collect():
    """新闻收藏"""

    # 判断用户是否登录
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg='用户未登录')

    # 获取参数
    news_id = request.json.get('news_id')
    action = request.json.get('action')

    if not all([news_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')

    # 判断参数
    if action not in ('collect', 'cancel_collect'):
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')

    try:
        news_id = int(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')

    # 查询新闻，判断新闻是否存在
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询数据失败')

    if not news:
        return jsonify(errno=RET.NODATA, errmsg='新闻数据不存在')

    if action == 'cancel_collect':
        # 取消收藏
        if news in user.collection_news:
            user.collection_news.remove(news)
    else:
        # 收藏新闻
        user.collection_news.append(news)

    return jsonify(errno=RET.OK, errmsg='操作成功')


@news_blue.route('/<int:news_id>')
@user_login_data
def news_detail(news_id):
    """新闻详情视图"""

    news = None
    try:
        news = News.query.filter_by(id=news_id).first()
    except Exception as e:
        current_app.logger.error(e)
        abort(404)

    if not news:
        # 返回数据未找到的页面
        abort(404)

    news.clicks += 1  # 记录访问量

    # 获取点击排行数据
    news_list = None
    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)

    click_news_list = []
    for click_news in news_list if news_list else []:
        click_news_list.append(click_news.to_basic_dict())

    # 获取当前新闻的评论
    comments = []
    try:
        comments = Comment.query.filter_by(news_id=news_id).order_by(Comment.create_time.desc()).all()
    except Exception as e:
        current_app.logger.error(e)

    comment_like_ids = []
    if g.user:
        # 如果当前用户登录
        try:
            comment_ids = [comment.id for comment in comments]
            if len(comment_ids) > 0:
                # 获取当前用户在当前新闻的所有评论点赞的记录
                comment_likes = CommentLike.query.filter(CommentLike.comment_id.in_(comment_ids), CommentLike.user_id==g.user.id).all()
                # 取出记录中所有的评论id
                comment_like_ids = [comment_like.comment_id for comment_like in comment_likes]
        except Exception as e:
            current_app.logger.error(e)


    comment_list = []
    for comment in comments if comments else []:
        comment_dict = comment.to_dict()
        comment_dict['is_like'] = False
        # 判断用户是否点赞该评论
        if g.user and comment_dict.get('id') in comment_like_ids:
            comment_dict['is_like'] = True
        comment_list.append(comment_dict)

    # 当前登录的用户是否关注当前新闻作者
    is_followed = False

    # 判断用户是否收藏过该新闻
    is_collected = False
    # print(news.to_dict())
    # print(news.user)
    if g.user:
        if news in g.user.collection_news:
            is_collected = True
        if news.user.followers.filter(User.id == g.user.id).count() > 0:
            is_followed = True

    data = {
        'user': g.user.to_dict() if g.user else None,
        'news': news.to_dict(),
        'click_news_list': click_news_list,
        'is_collected': is_collected,
        'comments': comment_list,
        'is_followed': is_followed
    }

    return render_template('news/detail.html', data=data)
