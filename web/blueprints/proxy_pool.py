# coding: utf-8

from random import choice
from flask import Blueprint, g, request

from web.core import get_redis_db

bp = Blueprint("proxypool", __name__)


REDIS_KEY = 'proxies'


def _get_conn():
    if not hasattr(g, 'redis'):
        g.redis = get_redis_db()
    return g.redis


def _get_ip():
    conn = _get_conn()
    result = conn.zrangebyscore(REDIS_KEY, 100, 100)
    if len(result):
        return choice(result)
    else:
        result = conn.zrevrange(REDIS_KEY, 0, 100)
        if len(result):
            return choice(result)
        else:
            return "empty"


@bp.route("/ip")
def get_user_ip():
    """
        获取当前访问ip
    """
    # ip = request.remote_addr
    ip = request.headers['X-Real-Ip']
    return ip


@bp.route("/IPProxy")
def index():
    return "<h1>Welcome to My Proxy Pool System</h1>"


@bp.route("/IPProxy/get")
def get_ip():
    ip = _get_ip()
    return ip


@bp.route("/IPProxy/count")
def get_ip_count():
    conn = _get_conn()
    return str(conn.zcard(REDIS_KEY))
