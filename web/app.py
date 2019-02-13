# coding: utf-8

from flask import Flask
from werkzeug.utils import find_modules

from web import config

def create_app():
    app = Flask(__name__)

    app.config.from_mapping(config)
    
    register_blueprints(app, 'web.blueprints')


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
