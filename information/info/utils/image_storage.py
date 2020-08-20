import logging

from qiniu import Auth, put_data


access_key = 'uc2U36YPfZG7pVai_YWyEwAZ35LgszUtm1_p6a7s'
secret_key = '4L1AcR7Z1wI-VVqhNsULSTF0DL2MrurdcXsK9oSg'

# 上传的空间名称
bucket_name = '840017951'


def storage(data):
    """七牛云存储上传文件接口"""

    if not data:
        return data

    try:
        # 构建鉴权对象
        q = Auth(access_key, secret_key)

        # 生成上传 Token，可以指定过期时间等
        token = q.upload_token(bucket_name)

        # 上传文件
        ret, info = put_data(token, None, data)
        # print(ret, info)

    except Exception as e:
        logging.error(e)
        raise e

    if info and info.status_code != 200:
        raise Exception("上传文件到七牛失败")

    # 返回七牛中保存的图片名称，即访问七牛的图片路径
    return ret["key"]


if __name__ == '__main__':
    file_name = input("请输入上传的文件：")
    # with open(file_name, 'rb') as f:
    #     storage(f.read())

    # print('%011d' % 0)