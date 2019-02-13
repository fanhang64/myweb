# coding: utf-8

from flask.cli import main

from web.app import create_app


app = create_app()


if __name__ == '__main__':
    main()
