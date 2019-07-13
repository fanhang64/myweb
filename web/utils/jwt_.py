import time
import logging

import jwt

from web.config import Config
from web.exceptions import TokenExpireErr

SECRET = Config.SECRET

logger = logging.getLogger(__name__)


def encode(uid, open_id=None, expire_in=24 * 30):
    payload = {
        'uid': uid,
        'open_id': open_id,
        'exp': int(time.time()) + 3600 * expire_in
    }
    encoded_jwt = jwt.encode(
        payload,
        SECRET
    )
    return encoded_jwt


def decode(jwt_token):
    try:
        decoded = jwt.decode(jwt_token, SECRET)
    except jwt.ExpiredSignature:
        raise TokenExpireErr
    return decoded
