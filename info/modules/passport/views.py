from flask import request, abort, current_app, make_response

import constants
from info import redis_store
from info.modules.passport import passport_blu
from info.utils.captcha.captcha import captcha


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
