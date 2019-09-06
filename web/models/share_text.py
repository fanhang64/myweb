from datetime import datetime

from web.core import db


class ShareCode(db.Model):
    __tablename__ = 'share_code'

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, comment='分享内容')
    code = db.Column(db.VARCHAR(64))
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())
