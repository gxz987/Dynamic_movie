from flask import request, abort, current_app, make_response, json

import constants
from info import redis_store
from info.modules.passport import passport_blu
from info.utils.captcha.captcha import captcha


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
    # 1.
    # dict_data = json.loads(request.data)  # request.data 得到的是一个字符串类型
    dict_data = request.json  # request.json 是flask中自带的，得到的结果是字典类型
    mobile = dict_data.get("mobile")
    image_code = dict_data.get("image_code")
    image_code_id = dict_data.get("image_code_id")
    # Todo 待完成



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
    # 1.
    image_code_id = request.args.get("imageCodeId")
    # 2.
    if not image_code_id:
        abort(404)
    # 3.
    _, text, image = captcha.generate_captcha()
    # 4.
    try:
        redis_store.setex("ImageCodeId_" + image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)
    except Exception as e:
        current_app.logger.error(e)
        abort(500)
    # 5.
    response = make_response(image)
    response.headers["Content-Type"] = "image/jpg"
    return response
