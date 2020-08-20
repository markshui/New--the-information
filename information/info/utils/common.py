# 公用的自定义工具
import functools

from flask import session, current_app, g


def do_index_class(index):
    """自定义过滤器，过滤点击排序html的class"""

    if index == 1:
        return "first"
    elif index == 2:
        return "second"
    elif index == 3:
        return "third"
    else:
        return ""


def user_login_data(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        # 获取当前登录用户的id
        user_id = session.get('user_id')
        # 获取id获取用户信息
        user = None
        try:
            from info.models import User
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)

        g.user = user
        return f(*args, **kwargs)

    return wrapper