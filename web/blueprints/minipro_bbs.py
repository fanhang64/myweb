import json
from urllib.parse import urlencode, urljoin

import requests
from flask import Blueprint, request
from flask.views import MethodView

from web.config import Config
from web.core import db
from web.models.minipro_bbs import Post, PostImage,\
     PostTopic, User, PostFavor, PostComment
from web.forms.minipro_bbs import PostForm, PostFavorForm, PostCommentForm
from web.exceptions import CustomBaseException, FormValidationError, ParameterError
from web.utils import jwt_


bp = Blueprint('minipro', __name__, url_prefix='/minipro')


@bp.route("/auth", methods=['POST'])
def auth():
    req_data = request.json
    code = req_data.get('code')
    if not code:
        return
    data = {
        'appid': Config.AppId,
        'secret': Config.AppSecret,
        'js_code': code,
        'grant_type': 'authorization_code'
    }

    url = 'https://api.weixin.qq.com/sns/jscode2session?'
    req_url = url + urlencode(data)
    try:
        res = requests.get(req_url).json()
        print(res)
        return res
    except:
        raise CustomBaseException
    return {}


@bp.route("/wx_login", methods=['POST'])
def wx_login():
    req_data = request.json
    openid = req_data.get('openid')
    if not openid:
        raise ParameterError('缺少参数openid')
    nickname = req_data.get('nickname')
    avatar_url = req_data.get('avatar_url')
    phone = req_data.get('phone')

    user = User.query.filter_by(open_id=openid).first()
    if not user:
        user = User()
        user.open_id = openid
        user.phone = phone
        user.nickname = nickname
        user.avatar = avatar_url
        db.session.add(user)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            return {'code': -1, 'msg': '生成token失败'}
    token = jwt_.encode(user.id, openid).decode()
    return {'token': token, 'user_id': user.id}


@bp.route("/users", methods=['GET', 'POST'])
def users():
    pass


@bp.route("/post/topic/", methods=['GET'])
def topic():
    res = []
    pt_list = PostTopic.query.all()
    for x in pt_list:
        res.append({
            'id': x.id,
            'name': x.name
        })
    return res

@bp.route("/user/<int:uid>/posts")
def user_post(uid):
    if not uid:
        raise ParameterError
    res = []
    favor = request.args.get('favor')
    comment = request.args.get('comment')
    limit = request.args.get('limit')
    since_id = request.args.get('since_id', type=int)
    if favor:
        post_favor = PostFavor.query\
            .filter(PostFavor.from_user_id == uid)\
            .order_by(PostFavor.id.desc())\
            .with_entities(PostFavor.post_id)
        post_ids = [x[0] for x in post_favor]
        query = Post.query.filter(Post.id.in_(post_ids))
        if since_id and since_id > 0:
            query = query.filter(PostFavor.id < since_id)
    elif comment:
        res = []
        query = PostComment.query\
            .filter(PostComment.uid == uid)\
            .order_by(PostComment.id.desc())
        if limit:
            query = query.limit(limit)
        if since_id and since_id > 0:
            query = query.filter(PostComment.id < since_id)
        post_comments = query.all()
        for x in post_comments:
            d = {
                'post_id': x.post_id,
                'content': x.content,
            }
            if x.replied_id:
                replied = PostComment.query.filter_by(id=x.replied_id).first()
                d['replier'] = replied.get_author_info()
                d['subject'] = replied.content
            else:
                post = x.post
                user = User.query.filter(User.id == post.user_id).first()
                d['replier'] = {
                    'nickname': user.nickname,
                    'avatar': user.avatar,
                    'id': user.id
                }
                d['subject'] = post.content
            res.append(d)
        return res
    else:
        query = Post.query.filter(Post.user_id == uid).order_by(Post.id.desc())
        if since_id and since_id > 0:
            query = query.filter(Post.id < since_id)
    if limit:
        query = query.limit(limit)
    posts = query.all()
    for post in posts:
        images = post.get_images()
        r = post.to_dict()
        r['images'] = images
        user = post.user
        r['author'] = {
            'nickname': user.nickname,
            'avatar': user.avatar
        }
        location = post.location
        r['location'] = json.loads(location) if location else None
        r['styled'] = [{'tag': True, 'text': post.content}]
        favors = post.get_favors_count()
        comments = post.get_comments_count()
        stats = {'favored': False, 'favors': favors, 'comments': comments}
        r['stats'] = stats
        res.append(r)
    return res


@bp.route("/post/comments", methods=['POST'])
def create_comments():
    data = request.json
    uid = data.get('uid')
    post_id = data.get('post_id')
    content = data.get('content')
    replied_id = data.get('replied_id')
    to_uid = data.get('to_uid')
    form = PostCommentForm(data=request.json)
    if form.validate():
        comment = PostComment(uid=uid, post_id=post_id, content=content)
        if replied_id:
            post_comment = PostComment.query.filter_by(id=replied_id).first()
            if not post_comment:
                raise CustomBaseException
            comment.replied = post_comment
            comment.to_uid = to_uid
        db.session.add(comment)
        db.session.commit()
        user = User.query.filter_by(id=uid).first()
        d = comment.to_dict()
        if user:
            d['author'] = {
                'nickname': user.nickname,
                'avatar': user.avatar,
                'id': uid
            }
        d['reply_list'] = []
        return d
    raise FormValidationError(form)


def get_comment_info(post_comment):
    res = {}
    user = User.query.filter_by(id=post_comment.uid).first()
    if user:
        res['author'] = post_comment.get_author_info()
    d = post_comment.to_dict()
    res.update(d)
    replies = post_comment.replies
    res['reply_list'] = []

    for x in replies:
        data = x.to_dict()
        data['author'] = x.get_author_info()
        to_user = User.query.filter_by(id=x.to_uid).first()
        if to_user:
            data['replier'] = {'nickname': to_user.nickname, 'avatar': to_user.avatar}
        res['reply_list'].append(data)
    return res
        

@bp.route("/post/<int:post_id>/comments", methods=['GET'])
def comments(post_id):
    if not post_id:
        return
    res = []
    post_comments = PostComment.query\
        .filter(PostComment.post_id == post_id)\
        .filter(PostComment.replied_id.is_(None))\
        .order_by(PostComment.id.desc()).all()
    for x in post_comments:
        d = get_comment_info(x)
        res.append(d)
    return res


@bp.route("/post/comments/<int:comment_id>", methods=['DELETE'])
def post_comments(comment_id):
    if not comment_id:
        raise ParameterError('缺少comment_id参数')
    query = PostComment.query.filter(PostComment.id==comment_id)
    query.delete()
    db.session.commit()
    return {}


class PostFavorView(MethodView):
    def get(self):
        post_id = request.args.get('post_id')
        user_id = request.args.get('user_id')
        if post_id:
            pass
        if user_id:
            post_favor_list = PostFavor.query\
                .filter_by(from_user_id=user_id)\
                .order_by(PostFavor.id.desc())\
                .with_entities(PostFavor.post_id)
            post_id_list = [x[0] for x in post_favor_list]   
            return post_id_list
        raise ParameterError

    def post(self):
        req_data = request.json
        form = PostFavorForm(data=req_data)
        if form.validate():
            post_favor = PostFavor()
            from_user_id = req_data.get('from_user_id')
            post_favor.from_user_id = from_user_id
            user = User.query.filter_by(id=from_user_id).first()
            post_favor.from_user_name = user.nickname
            post_favor.to_user_id = req_data.get('to_user_id')
            post_favor.post_id = req_data.get('post_id')
            db.session.add(post_favor)
            db.session.commit()
            return {}
        raise FormValidationError(form)
    
    def delete(self, post_id):
        user_id = request.args.get('user_id')  # 点赞人
        if post_id and user_id:
            post_favor = PostFavor.query.filter_by(post_id=post_id,\
                from_user_id=user_id).first()
            if post_favor:
                db.session.delete(post_favor)
                db.session.commit()
            return {}
        raise ParameterError


class PostView(MethodView):
    def get(self, post_id):
        limit = request.args.get('limit')
        filter_args = request.args.get('filter')
        since_post_id = request.args.get('since_id', type=int)
        topic_id = request.args.get('topic_id')
    
        res = []
        query = Post.query.order_by(Post.id.desc())
        if post_id:
            query = query.filter_by(id=post_id)
        if filter_args == 'val':
            query = query.filter_by(status=2)
        elif filter_args == 'top':
            query = query.filter_by(status=3)
        if topic_id:
            query = query.filter(Post.topic_id == topic_id)
        if since_post_id and since_post_id > 0:
            query = query.filter(Post.id < since_post_id)
        if limit:
            query = query.limit(limit)

        posts = query.all()
        for post in posts:
            images = post.get_images()
            r = post.to_dict()
            r['images'] = images
            user = post.user
            r['author'] = {
                'nickname': user.nickname,
                'avatar': user.avatar
            }
            location = post.location
            r['location'] = json.loads(location) if location else None
            r['styled'] = [{'tag': True, 'text': post.content}]
            favors = post.get_favors_count()
            comments = post.get_comments_count()
            stats = {'favored': False, 'favors': favors, 'comments': comments}
            r['stats'] = stats
            res.append(r)
        return res
    
    def post(self):
        req_data = request.json
        form = PostForm(data=req_data)
        if form.validate():
            post_obj = Post()
            post_obj.title = req_data.get('title')
            post_obj.content = req_data.get('content')
            post_obj.user_id = req_data.get('author_id')
            post_obj.location = req_data.get('location')
            post_obj.topic_id = req_data.get('topic_id')
            db.session.add(post_obj)
            db.session.flush()
            media = req_data.get('media', {})

            images = media.get('path', [])
            for img_url in images:
                post_image = PostImage(image_url=img_url, post_id=post_obj.id)
                db.session.add(post_image)
            db.session.commit()
            return {}
        raise FormValidationError(form)
    
    def put(self, post_id):
        req_data = request.json
        user_id = req_data.get('user_id')
        if post_id:
            post = Post.query.filter_by(id=post_id, user_id=user_id).first()
            post.title = req_data.get('title')
            post.content = req_data.get('content')
            post.location = req_data.get('location')
            db.session.commit()
            return {}
        raise ParameterError

    def delete(self, post_id):
        if post_id:
            post = Post.query.filter_by(id=post_id).first()
            if post:
                post.status = -1
                db.session.commit()
            return {}
        raise ParameterError


user_view = PostView.as_view('post')
bp.add_url_rule('/post/', defaults={'post_id': None},
                 view_func=user_view, methods=['GET',])
bp.add_url_rule('/post/', view_func=user_view, methods=['POST',])
bp.add_url_rule('/post/<int:post_id>', view_func=user_view,
                 methods=['GET', 'PUT', 'DELETE'])

post_favor_view = PostFavorView.as_view('post_favor')
bp.add_url_rule('/post/favors/', view_func=post_favor_view, methods=['GET', 'POST'])
bp.add_url_rule('/post/favors/<int:post_id>', view_func=post_favor_view, methods=['DELETE'])
