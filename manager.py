# coding: utf-8

import click
from flask.cli import main

from web.app import create_app
from web.core import db


app = create_app()


@app.cli.command()
@click.option('--drop', default=False)
def init_db(drop):
    if drop:
        db.drop_all()
    db.create_all()


if __name__ == '__main__':
    main()
