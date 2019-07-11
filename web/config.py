
class Config:
    DEBUG = True
    LOG_PATH = '/root/code/pro/myflask/logs/all.logs'

    # redis
    REDIS_URL = 'redis://:123@127.0.0.1:6379'
    REDIS_DB = 1
    
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123@localhost/minipro_bbs'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
