import random
import re
from datetime import datetime

from flask import request, current_app, make_response, jsonify, session

from info import redis_store, db
from info.libs.yuntongxun.sms import CCP
from info.models import User
from info.utils.captcha.captcha import captcha
from info import constants
from info.utils.response_code import RET
from . import passport_blue


# /passport/logout
@passport_blue.route('/logout', methods=['POST'])
def logout():
    """
    退出登录
    :return:
    """
    # pop可以移除session中的数据(dict)
    # pop会有一个返回值，如果移除的key不存在，则返回None
    session.pop('user_id', None)
    session.pop('mobile', None)
    session.pop('nick_name', None)
    session.pop('is_admin', None)

    return jsonify(errno=RET.OK, errmsg='退出成功')


# /passport/login
@passport_blue.route('/login', methods=['POST'])
def login():
    """
    用户登录
    1、获取登录请求参数
    2、校验参数
    3、查询该用户帐号在数据库中是否已注册
    4、校验用户密码
    5、保存用户登录状态
    6、返回登录成功的结果
    :return:
    """

    # 1、获取用户登录请求的参数
    json_data = request.json
    mobile = json_data.get('mobile')
    password = json_data.get('password')

    # 2、校验参数
    if not all([mobile, password]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不全')

    if not re.match('^1[35678][0-9]{9}$', mobile):
        return jsonify(errno=RET.DATAERR, errmsg='手机号格式不正确')

    if len(password) < 6:
        return jsonify(errno=RET.DATAERR, errmsg='密码至少6位数')

    # 3、查询该用户帐号在数据库中是否存在
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询数据错误')

    if not user:
        return jsonify(errno=RET.USERERR, errmsg='用户名或密码不正确')

    # 4、校验用户密码
    if not user.check_passowrd(password):
        return jsonify(errno=RET.PWDERR, errmsg='用户名或密码不正确')

    # 5、保存用户登录状态
    session['user_id'] = user.id
    session['nick_name'] = user.nick_name
    session['mobile'] = user.mobile

    # 6、保存用户最后一次登录的时间
    user.last_login = datetime.now()

    # 如果在视图函数中，修改模型类上的属性，需要commit到数据库保存
    # 如果在SQLAlchemy有过相关配置，就不需要写 db.session.commit()
    # try:
    #     db.session.commit()
    # except Exception as e:
    #     current_app.logger.error(e)

    # 7、用户登录成功
    return jsonify(errno=RET.OK, errmsg='登录成功')


# /passport/register
@passport_blue.route('/register', methods=['POST'])
def register():
    """
    新用户注册
    1、获取表单提交的数据
    2、校验数据
    3、从redis中获取指定手机号对应的短信验证码并校验
    4、初始化user模型类，并添加数据到数据库中
    5、保存当前用户的状态
    6、返回注册的结果
    :return:
    """

    # 1、获取表单提交的数据
    json_data = request.json
    mobile = json_data.get('mobile')
    sms_code = json_data.get('sms_code')
    password = json_data.get('password')

    # 2、校验数据
    if not all([mobile, sms_code, password]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不全')
    if not re.match('^1[35678][0-9]{9}$', mobile):
        return jsonify(errno=RET.DATAERR, errmsg='手机号不存在')
    if len(password) < 6:
        return jsonify(errno=RET.DATAERR, errmsg='密码不能少于6位数')

    # 3、从redis中获取指定手机号对应的短信验证码
    try:
        real_sms_code = redis_store.get('SMS_' + mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg='获取验证码失败')
    # 判断验证码是否过期
    if not real_sms_code:
        return jsonify(errno=RET.NODATA, errmsg='短信验证码过期')
    # 用户输入的检验验证码是否正确
    if sms_code != real_sms_code:
        return jsonify(errno=RET.DATAERR, errmsg='短信验证码错误')

    # 4、初始化user模型类，并添加数据到数据库中
    user = User()
    user.nick_name = mobile
    user.mobile = mobile
    user.last_login = datetime.now()
    # 对密码进行加密处理
    user.password = password
    #
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg='数据保存失败')

    # 5、保存当前用户的状态
    session['user_id'] = user.id
    session['nick_name'] = user.nick_name
    session['mobile'] = user.mobile

    # 6、返回注册的结果
    return jsonify(errno=RET.OK, errmsg='注册成功')


# /passport/sms_code
@passport_blue.route('/sms_code', methods=['POST'])
def send_sms_code():
    """
    发送手机短信验证码逻辑：
    1、接收参数并判断是否有值
    2、校验手机号是否正确
    3、通过传入的图片编码去redis中查询真实的图片验证码内容
    4、判断验证码是否过期
    5、校验图片验证码内容
    6、生成短信验证码的内容并发送短信
    7、将短信验证码内容保存到redis中
    8、返回发送成功的响应
    :return:
    """

    # 1、接收参数并判断是否有值
    # '{"mobile": "18666872096", "image_code": "123456", "image_code_id": "56a52696-26c2-4955-808b-b3ac03cbaeeb"}'
    data_dict = request.json
    mobile = data_dict.get('mobile')
    image_code = data_dict.get('image_code')
    image_code_id = data_dict.get('image_code_id')

    if not all([mobile, image_code, image_code_id]):
        # 参数不全
        return jsonify(error=RET.PARAMERR, errmsg='参数不全')

    # 2、校验手机号是否正确
    if not re.match('^1[35678][0-9]{9}$', mobile):
        # 提示手机号不正确
        return jsonify(errno=RET.DATAERR, errmsg='手机号不正确')

    # 3、通过传入的图片编码去redis中查询真实的图片验证码内容
    try:
        real_image_code = redis_store.get('ImageCodeId_' + image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取图片验证码失败')

    # 4、判断验证码是否过期
    if not real_image_code:
        # 获取图片验证码内容失败，已过期
        return jsonify(errno=RET.NODATA, errmsg='获取图片验证码失败')

    # 5、校验用户输入的验证码是否正确
    if image_code.upper() != real_image_code.upper():
        # 验证码输入错误
        return jsonify(errno=RET.DATAERR, errmsg='验证码输入错误')

    # 校验该手机是否已注册
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据库查询错误')
    if user:
        return jsonify(errno=RET.DATAEXIST, errmsg='该手机号已被注册')

    # 6、生成短信码的内容并发送短信
    sms_code = '%06d' % random.randint(0, 999999)
    current_app.logger.debug('短信验证码的内容：%s' % sms_code)
    ccp = CCP()
    result = ccp.send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES / 60], '1')
    if result != 0:
        # 发送短信验证码失败
        return jsonify(errno=RET.THIRDERR, errmsg='发送短信验证码失败')

    # 7、将短信码内容保存到redis中
    try:
        redis_store.set('SMS_' + mobile, sms_code, constants.SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error('保存短信验证码失败')
        # 保存短信验证码失败
        return jsonify(errno=RET.DBERR, errmsg='保存短信验证码失败')

    # 8、返回发送成功后的响应
    return jsonify(errno=RET.OK, errmsg='发送成功')


# /passport/image_code
@passport_blue.route('/image_code')
def get_image_code():
    """
    生成图片验证码
    :return:
    """

    # 1.获取当前图片编号id
    image_code_id = request.args.get('imageCodeId', None)
    # 2.生成验证码
    name, text, image = captcha.generate_captcha()
    try:
        # 3.保存当前生成的图片验证码内容
        redis_store.set('ImageCodeId_' + image_code_id, text, ex=constants.IMAGE_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return make_response(jsonify(errorno=RET.DATAERR, errmsg='保存图片验证码失败'))

    # 4.返回图片验证码
    resp = make_response(image)
    resp.headers['Content-Type'] = 'image/jpg'
    return resp
