import random
import re
from datetime import datetime

from flask import request, abort, current_app, make_response, jsonify, session

from info import constants
from info import redis_store, db
from info.modules.passport import passport_blu
from info.utils.captcha.captcha import captcha
from info.utils.response_code import RET
from info.libs.yuntongxun.sms import CCP
from info.models import User
from werkzeug.security import generate_password_hash


@passport_blu.route('/logout')
def logout():
    """
    退出功能:删除session
    :return:
    """
    session.pop("is_admin", None)
    session.pop("user_id", None)
    return jsonify(errno=RET.OK, errmsg="退出成功")


@passport_blu.route('/login', methods=['POST'])
def login():
    """
    登录功能
    1.接收参数
    2.全局校验
    3.校验手机好格式（正则）
    4、校验密码
    5、保持状态
    6.给前端响应

    :return:
    """
    dict_data = request.json
    mobile = dict_data.get("mobile")
    passport = dict_data.get("passport")

    if not all([mobile, passport]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    if not re.match(r"1[35678]\d{9}", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机格式不正确")

    try:
        user = User.query.filter(User.mobile==mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询错误")

    if not user:
        return jsonify(errno=RET.NODATA, errmsg="该用户还未注册")

    # user_password = user.check_passowrd(user.password_hash)
    # if user_password != passport:
    if not user.check_passowrd(passport):
        return jsonify(errno=RET.DATAERR, errmsg="密码输入错误")

    # 更新最后登录时间
    user.last_login = datetime.now()
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库保存失败")

    # 保持用户登录状态
    session["user_id"] = user.id

    return jsonify(errno=RET.OK, errmsg="登录成功")


@passport_blu.route('/register', methods=["POST"])
def register():
    """注册
    1.接收参数 mobile smscode password
    2.整体校验参数的完整性
    3.手机号正则验证
    4.从redis中通过手机号取出真实的短信验证码
    5.和用户输入的验证码进行校验
    6.初始化一个User()对象，并添加数据
    7.返回响应
    """
    # 1.接收参数 mobile smscode password
    dict_data = request.json
    mobile = dict_data.get("mobile")
    smscode = dict_data.get("smscode")
    password = dict_data.get("password")

    # 2.整体校验参数的完整性
    if not all([mobile, smscode, password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    # 3.手机号正则验证
    if not re.match(r"1[35678]\d{9}", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机格式不正确")
    # 4.从redis中通过手机号取出真实的短信验证码
    try:
        real_sms_code = redis_store.get("SMS_" + mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询失败")

    # 5.和用户输入的验证码进行校验
    if not real_sms_code:
        return jsonify(errno=RET.NODATA, errmsg="短信验证码已过期")

    if real_sms_code != smscode:
        return jsonify(errno=RET.DATAERR, errmsg="短信验证码输入不正确")
    # 核心代码：6.初始化一个User()对象，并添加数据
    user = User()
    user.nick_name = mobile
    # user.password_hash = generate_password_hash(password)  # 第一种方式为密码加密
    user.password = password  # 第二种方式调用models.py为密码加密
    user.mobile = mobile

    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库保存失败")

    # 7.session 保持用户登录状态
    session["user_id"] = user.id

    # 8.给前端一个响应
    return jsonify(errno=RET.OK, errmsg="注册成功")


@passport_blu.route('/sms_code', methods=["POST"])
def send_sms_code():
    """发送短信的逻辑
    1.获取参数()：手机号mobile，图片验证码内容image_code，图片验证码的编号image_code_id（随机值）
    2、校验参数：model 正则（参数是否符合规则，判断是否有值）
    3、先从redis中取出真实的验证内容（通过image_code_id查询出来的验证码），
        与用户输入的验证码内容进行对比，如果不一致，返回验证码输入错误
    4.如果通过手机校验和图片验证码验证，定义一个随机的6位手机验证码（随机数据）
    5.调用云通讯发送手机验证码
    6、将手机验证码保存到redis中
    7.告知发送结果，给前段一个响应
    """
    # 1.接收前端传入的json类型的数据
    # dict_data = json.loads(request.data)  # request.data 得到的是一个字符串类型
    dict_data = request.json  # request.json 是flask中自带的，得到的结果是字典类型

    # 2.获取参数
    mobile = dict_data.get("mobile")
    image_code = dict_data.get("image_code")
    image_code_id = dict_data.get("image_code_id")

    # 3.先全局检验（判断mobile,image_code, image_code_id是否都存在，若不全，则返回参数不全）
    if not all([mobile, image_code, image_code_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    # 4.正则验证手机号（到达这，说明手机号已填写）
    if not re.match(r"1[35678]\d{9}", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号格式不正确")

    # 5.验证图片验证码（到达这，说明手机已验证通过）
    # 取出真实的验证码
    try:
        real_image_code = redis_store.get("ImageCodeId_" + image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询失败")

    # 验证
    if not real_image_code:
        return jsonify(errno=RET.NODATA, errmsg="图片验证码已过期")

    if image_code.upper() != real_image_code.upper():
        return jsonify(errno=RET.DATAERR, errmsg="图片验证码输入错误")

    # 6.定义一个随机的6位手机验证码
    sms_code_str = "%06d" % random.randint(0, 999999)
    current_app.logger.info("短信验证码为%s" % sms_code_str)

    # result = CCP().send_template_sms(mobile, [sms_code_str, constants.SMS_CODE_REDIS_EXPIRES / 60], 1)
    #
    # if result != 0:
    #     return jsonify(errno=RET.THIRDERR, errmsg="短信验证码发送失败")

    # 7.将手机验证码保存到redis中
    try:
        redis_store.setex("SMS_" + mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code_str)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="手机验证码保存失败")

    # 8.给前段一个响应(到达这，说明已通过验证并已保存手机验证码)
    return jsonify(errno=RET.OK, errmsg="短信验证码发送成功")


@passport_blu.route('/image_code')
def get_image_code():
    # GET /passport/image_code?imageCodeId = 672dc752 - efa0 - 4d28 - ba07 - a7abfa3a24d5
    """
    1.接收参数（接收随机的字符串）
    2、校验参数是否存在
    3、生成验证码  captche
    4、把随机的字符串和生成的文本验证码以key，value的形式保存到redis
    5、把图片验证码返回给浏览器
    :return:
    """
    # 1.接收参数（接收随机的字符串）
    image_code_id = request.args.get("imageCodeId")
    # 2.校验参数是否存在,不存在则返回404
    if not image_code_id:
        abort(404)
    # 3.生成验证码  captche
    _, text, image = captcha.generate_captcha()
    current_app.logger.info("图片验证码为%s" % text)
    # 4.把随机的字符串和生成的文本验证码以key，value的形式保存到redis
    try:
        redis_store.setex("ImageCodeId_" + image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)
    except Exception as e:
        current_app.logger.error(e)
        abort(500)
    # 5.把图片验证码返回给浏览器，修改Content-Type类型
    response = make_response(image)
    response.headers["Content-Type"] = "image/jpg"
    return response
