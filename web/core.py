import redis

from web import config


_redis_db = None


def get_redis_db():
    global _redis_db
    if not _redis_db:
        pool = redis.ConnectionPool.from_url(config['redis']['uri'],
                                             decode_components=config['redis'].get('decode_components', True))
        r = redis.Redis(connection_pool=pool)
        _redis_db = r

    return _redis_db
