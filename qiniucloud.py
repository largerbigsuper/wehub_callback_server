import os
import datetime
import uuid
import logging

from qiniu import Auth, put_data, put_file

# 图片样式
beep_logo_cover = '-beep_logo'

class QiniuService:
    # 构建鉴权对象
    QINIU_ACCESS_KEY = 'r9Wn86UUlqWqRbt1E4Mvl8lPXPcZpSSH1t2n0MR6'
    QINIU_SECRET_KEY = 'OdRXdCnUSpDdkY5n4-PUQT3psAm2zJMiHvgNfU_S'
    QINIU_BUCKET_NAME_DICT = {
        'image': 'images-beepcrypto',
        'video': 'videos-beepcrypto'
    }
    QINIU_BUCKET_DOMAIN_DICT = {
        'image': 'https://cdn.beepcrypto.com/',
        'video': 'https://cdn.beepcrypto.com/'
    }
    access_key = QINIU_ACCESS_KEY
    secret_key = QINIU_SECRET_KEY
    qiniuAuth = Auth(access_key, secret_key)
    bucket_name_dict = QINIU_BUCKET_NAME_DICT
    bucket_domain_dict = QINIU_BUCKET_DOMAIN_DICT
    logger = logging.getLogger('qiniu')

    @classmethod
    def get_bucket_name(cls, file_type):
        return cls.bucket_name_dict[file_type]

    @classmethod
    def gen_app_upload_token(cls, bucket_name):
        """
        app 上传token生成
        :param bucket_name: 文件存储空间名
        :param filename: 上传到七牛后保存的文件名
        :param user_id: 用户user_id
        :return:
        """
        policy = {
            'fsizeLimit': 500 * 1024 * 1024
        }
        #3600为token过期时间，秒为单位。3600等于一小时
        token = cls.qiniuAuth.upload_token(bucket_name, None, 3600, policy)
        return token
    
    @classmethod
    def upload_local_image(cls, image_path):
        """上传本地图片
        """
        name = os.path.basename(image_path)
        # 构建鉴权对象
        token = cls.gen_app_upload_token(QiniuService.get_bucket_name('image'))
        ret, info = put_file(token, cls._new_name(name), image_path)
        if info.status_code == 200:
            base_url = '%s%s' % (QiniuService.bucket_domain_dict['image'], ret.get("key"))
            # 表示上传成功, 返回文件名
            return base_url
        else:
            # 上传失败
            raise Exception("上传七牛失败")

    @classmethod
    def upload_data(cls, file_data, save_name):
        """上传内存文件
        """
        # 构建鉴权对象
        token = cls.gen_app_upload_token(QiniuService.get_bucket_name('image'))
        ret, info = put_data(token, save_name, file_data.read())

        if info.status_code == 200:
            base_url = '%s%s' % (QiniuService.bucket_domain_dict['image'], ret.get("key"))
            # 表示上传成功, 返回文件名
            cls.logger.error('base_url: {}'.format(base_url))
            return base_url

        else:
            # 上传失败
            cls.logger.error('{} upload failed: {}, {}'.format(save_name, info, ret))
            raise Exception("上传七牛失败")


    @staticmethod
    def _new_name(name):
        new_name = "file/{0}/{1}.{2}".format(datetime.datetime.now().strftime("%Y/%m/%d"), str(uuid.uuid4()).replace('-', ''),
                                             name.split(".").pop())
        return new_name


def get_filename(filename):
    new_name = "file/{0}/{1}.{2}".format(datetime.datetime.now().strftime("%Y/%m/%d"), str(uuid.uuid4()).replace('-', ''),
                                            filename.split(".").pop())
    return new_name
