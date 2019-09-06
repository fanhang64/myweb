import os


class Config:
    DEBUG = True
    LOG_PATH = '/root/code/pro/myflask/logs/all.logs'
    SECRET = 'ab87a8d04e9cde2ad7c014fd2bbeeaae'

    # redis
    REDIS_URL = 'redis://:123@127.0.0.1:6379'
    REDIS_DB = 1
    
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123@localhost/minipro_bbs'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    AppId = 'wx4b5a9beb9ca390ef'
    AppSecret = '233d18b3ad200276f6c38ebe424488fd'

    ShareTextUrl = 'http://hapi.5ihouse.cn'
