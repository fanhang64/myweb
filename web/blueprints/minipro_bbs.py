import json
from urllib.parse import urlencode, urljoin

import requests
from flask import Blueprint, request
from flask.views import MethodView

from web.config import Config
from web.core import db
from web.models.minipro_bbs import Post, PostImage, PostTopic, User
from web.forms.minipro_bbs import PostForm
from web.exceptions import CustomBaseException, FormValidationError, ParameterError
from web.utils import jwt_


bp = Blueprint('minipro', __name__, url_prefix='/minipro')


@bp.route("/auth", methods=['POST'])
def auth():
    req_data = request.json
    code = req_data.get('code', "081QsvNn1PrBNp0okiQn1ellNn1QsvN7")
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
    user = User()
    user.open_id = open_id
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
    return {'token': token}


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

 
class PostView(MethodView):
    def get(self, post_id):
        limit = request.args.get('limit')
        filter_args = request.args.get('filter')
        since_post_id = request.args.get('since_id', type=int)
        topic_id = request.args.get('topic_id')
    
        res = []
        query = Post.query.order_by(Post.id.desc())
        if post_id:
            post = query.filter_by(id=post_id)

        if filter_args == 'val':
            query = query.filter_by(status=2)
        elif filter_args == 'top':
            query = query.filter_by(status=3)
        if topic_id:
            query = query.filter(Post.topic_id == topic_id)
        if since_post_id > 0:
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
                db.session.delete(post)
                db.session.commit()
            return {}
        raise ParameterError


user_view = PostView.as_view('post')
bp.add_url_rule('/post/', defaults={'post_id': None},
                 view_func=user_view, methods=['GET',])
bp.add_url_rule('/post/', view_func=user_view, methods=['POST',])
bp.add_url_rule('/post/<int:post_id>', view_func=user_view,
                 methods=['GET', 'PUT', 'DELETE'])
