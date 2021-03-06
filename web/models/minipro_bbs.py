from datetime import datetime

from sqlalchemy.dialects.mysql import TINYINT

from web.core import db


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    open_id = db.Column(db.VARCHAR(64), nullable=False)
    phone = db.Column(db.VARCHAR(11), nullable=False)
    nickname = db.Column(db.VARCHAR(32), nullable=False)
    avatar = db.Column(db.VARCHAR(256), default='', comment='头像')
    status = db.Column(TINYINT(2), default=0)
    is_admin = db.Column(TINYINT(2), default=0)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())

    posts = db.relationship('Post', backref=db.backref('user'), lazy=True)


class PostTopic(db.Model):
    __tablename__ = 'post_topic'

    id = db.Column(db.Integer, primary_key=True)
    name =  db.Column(db.VARCHAR(16), nullable=False, comment='标题')
    status = db.Column(TINYINT(2), default=0)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())

    posts = db.relationship('Post', backref=db.backref('topic'), lazy=True)


class Post(db.Model):
    __tablename__ = 'post'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.VARCHAR(64), nullable=True, comment='标题')
    content = db.Column(db.TEXT, comment='内容')
    post_type = db.Column(TINYINT(2), default=0, comment='1 精华帖 2 置顶帖')
    status = db.Column(TINYINT(2), default=0, comment='0 默认未审核, 1 审核通过 -1 删除') 
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())
    location = db.Column(db.JSON, nullable=True, comment='所在位置')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    images = db.relationship('PostImage', backref=db.backref('post'), lazy=True)

    topic_id = db.Column(db.Integer, db.ForeignKey('post_topic.id'))

    comments = db.relationship('PostComment', back_populates='post')

    def to_dict(self):
        keys = [x.name for x in self.__table__.columns]
        data = {key: getattr(self, key) for key in keys}
        return data
    
    def get_images(self):
        return [x.image_url for x in self.images]

    def get_favors_count(self):
        return PostFavor.query.filter_by(post_id=self.id).count()

    def get_comments_count(self):
        return PostComment.query.filter_by(post_id=self.id).count()


class PostImage(db.Model):
    __tablename__ = 'post_images'

    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.VARCHAR(256), nullable=True)
    status = db.Column(TINYINT(2), default=0)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())

    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))


class PostFavor(db.Model):
    __tablename__ = 'post_favor'

    id = db.Column(db.Integer, primary_key=True)
    from_user_id = db.Column(db.Integer, nullable=False, comment='点赞人id')
    from_user_name = db.Column(db.VARCHAR(32), nullable=False)
    to_user_id = db.Column(db.Integer, nullable=False, comment='被点赞人id')
    post_id = db.Column(db.Integer, nullable=False)
    status = db.Column(TINYINT(2), default=0)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())

    def to_dict(self):
        keys = [x.name for x in self.__table__.columns]
        data = {key: getattr(self, key) for key in keys}
        return data
    
    @classmethod
    def get_favors(cls, user_id, limit=20, since_id=None):
        res = []
        query = cls.query.filter_by(to_user_id=user_id)
        if since_id and since_id > 0:
            query = query.filter_by(cls.id < since_id)
        query = query.order_by(cls.id.desc())
        if limit:
            query = query.limit(limit)
        for x in query.all():
            post = Post.query.get(x.post_id)
            d = {
                'id': x.id,
                'created_at': x.created_at,
                'content': post.content,
                'status': x.status,
                'post_id': post.id,
            }
            user = User.query.filter_by(id=x.from_user_id).first()
            if user:
                d['author'] = {
                    'user_id': x.from_user_id,
                    'user_name': x.from_user_name,
                    'avatar': user.avatar
                }
            res.append(d)
        return res


class PostComment(db.Model):
    __tablename__  = 'post_comments'

    id = db.Column(db.Integer, primary_key=True)  # a huifu b: 123
    uid = db.Column(db.Integer, nullable=False, comment='用户id')
    content = db.Column(db.VARCHAR(32), nullable=True)
    status = db.Column(TINYINT(2), default=0)

    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    post = db.relationship('Post', back_populates='comments')

    replied = db.relationship('PostComment', back_populates='replies', remote_side=[id])  # 评论

    replied_id = db.Column(db.Integer, db.ForeignKey('post_comments.id'))  # 回复的comment id
    replies = db.relationship('PostComment', back_populates='replied', cascade='all, delete-orphan')

    to_uid = db.Column(db.Integer, nullable=False, comment='被回复人用户id')
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())

    def to_dict(self):
        keys = [x.name for x in self.__table__.columns]
        data = {key: getattr(self, key) for key in keys}
        return data

    def get_author_info(self):
        user = User.query.filter_by(id=self.uid).first()
        return {
            'nickname': user.nickname,
            'avatar': user.avatar,
            'id': self.id
        }

    @classmethod
    def get_comments(cls, user_id, limit=20, since_id=None):
        res = []
        query = cls.query.filter_by(to_uid=user_id)
        if since_id and since_id > 0:
            query = query.filter_by(cls.id < since_id)
        query = query.order_by(cls.id.desc())
        if limit:
            query = query.limit(limit)
        for x in query.all():
            post = x.post
            d = {
                'id': x.id,
                'created_at': x.created_at,
                'content': post.content,
                'status': x.status,
                'post_id': post.id,
            }
            user = User.query.filter_by(id=x.uid).first()
            if user:
                d['author'] = {
                    'user_id': user.id,
                    'user_name': user.nickname,
                    'avatar': user.avatar
                }
            res.append(d)
        return res


class Report(db.Model):
    __tablename__ = 'post_report'

    id = db.Column(db.Integer, primary_key=True)  # a huifu b: 123
    post_id = db.Column(db.Integer, nullable=False, comment='帖子id')
    status = db.Column(TINYINT(2), default=0)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())
