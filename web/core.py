import redis

from flask_sqlalchemy import SQLAlchemy

from web.config import Config


_redis_db = None


def get_redis_db():
    global _redis_db
    if not _redis_db:
        pool = redis.ConnectionPool.from_url(Config.REDIS_URL,
                                             decode_components=True)
        r = redis.Redis(connection_pool=pool)
        _redis_db = r

    return _redis_db


db = SQLAlchemy()
