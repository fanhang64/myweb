# coding: utf-8

import datetime
import traceback
import logging 
import sys
import json
from logging.handlers import RotatingFileHandler

from flask import Flask, jsonify, request
from werkzeug.utils import find_modules

from .config import Config

logger = logging.getLogger(__name__)


def create_app():
    app = Flask(__name__)
    print(Config)
    app.config.from_object(Config)

    init_log(app)
    register_blueprints(app, 'web.blueprints')
    register_after_request(app)
    register_err_handler(app)

    return app


def register_blueprints(app, path):
    def _import_string(import_name):
        import sys
        import_name = str(import_name).replace(':', '.')
        try:
            __import__(import_name)
        except ImportError:
            raise
        else:
            return sys.modules[import_name]

    for name in find_modules(path):
        mod = _import_string(name)
        if not hasattr(mod, 'bp'):
            continue
        urls = name.split('.')
        prefix = '/{}'.format(urls[-1])
        app.register_blueprint(mod.bp, url_prefix=prefix)


def init_log(app):
    fmt = "%(message)s"

    if app.config['DEBUG']:
        handler = logging.StreamHandler(sys.stdout)
    else:
        handler = RotatingFileHandler(app.config['LOG_PATH'], maxBytes=1024*2014*1024, backupCount=3)

    logging.basicConfig(
        level=logging.DEBUG,
        format=fmt,
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[handler]
    )

    logging.getLogger('myflask').setLevel(logging.WARNING)


def register_after_request(app):
    @app.after_request
    def log_response(resp):
        log_msg = {
            'url': request.path,
            'args': json.dumps(request.args),
            'req_time': datetime.datetime.now().isoformat(),
        }
        try:
            req_data = request.get_json()
            if req_data:
                log_msg['req_data'] = req_data
        except:
            pass
        try:
            resp_data = resp.data
            log_msg['resp_data'] = resp_data
        except:
            pass
        logger.debug(log_msg)
        return resp


def register_err_handler(app):
    @app.errorhandler(Exception)
    def handler_exception(err):
        print(traceback.format_exc())
        logger.error(traceback.format_exc())
        return jsonify(code=-1, msg='', error='server iternal err')

    @app.errorhandler(404)
    def handle_404(err):
        return jsonify(code=-2, mgs='', error='api not found')
