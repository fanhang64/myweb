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
from .core import db
from .utils import JsonResponse
from .exceptions import CustomBaseException, FormValidationError

logger = logging.getLogger(__name__)


class WebFlask(Flask):

    def make_response(self, rv):
        if isinstance(rv, (dict, list)):
            rv = JsonResponse(rv)
            return rv.to_response()
        return Flask.make_response(self, rv)


def create_app():
    app = WebFlask(__name__)
    print(Config)
    app.config.from_object(Config)

    init_log(app)
    register_blueprints(app, 'web.blueprints')
    register_before_request(app)
    register_after_request(app)
    register_err_handler(app)
    register_extensions(app)
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
        if hasattr(mod, 'bp'):
            app.register_blueprint(mod.bp)


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


def register_before_request(app):
    @app.before_request
    def aaa():
        aa = request.headers
        print(aa)


def register_after_request(app):
    pass


def register_err_handler(app):
    @app.errorhandler(CustomBaseException)
    def handler_exception(err):
        return jsonify(errcode=err.errcode, errmsg=err.errmsg, **err.kw)
    
    @app.errorhandler(FormValidationError)
    def form_validation_err_handler(e):
        return jsonify(errcode=e.errcode, errmsg=e.errmsg, errors=e.errors, **e.kw)

    @app.errorhandler(404)
    def handle_404(err):
        return jsonify(errcode=-2, errmsg='api not found')


def register_extensions(app):
    db.init_app(app)
