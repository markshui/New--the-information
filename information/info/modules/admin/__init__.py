from flask import Blueprint, request, url_for, session, redirect

admin_blue = Blueprint("admin", __name__, url_prefix="/admin")

from . import views


@admin_blue.before_request
def before_request():
    # 判断如果不是登录页面的请求
    if not request.url.endswith(url_for('admin.admin_login')):
        user_id = session.get('user_id', None)
        is_admin = session.get('is_admin', False)

        # 判断当前是否有用户登录，或者是否是管理员
        # 如果不是，则跳转到项目主页
        if not user_id or not is_admin:
            return redirect('/')