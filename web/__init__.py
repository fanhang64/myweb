# coding: utf-8


def get_config():
    import os
    import toml

    path = os.environ.get('FLASK_CONFIG')
    print(path)
    try:
        return toml.load(path)
    except FileNotFoundError:
        print(f"config file not found:{path}")
        raise


def init_log():
    import logging

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    console_handler = logging.StreamHandler
    logger.addHandler(console_handler)

config = get_config()
init_log()
