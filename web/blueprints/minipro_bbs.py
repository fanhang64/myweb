import json

from flask import Blueprint, request
from flask.views import MethodView

from web.core import db
from web.models.minipro_bbs import Post, PostImage
from web.forms.minipro_bbs import PostForm
from web.exceptions import CustomBaseException, FormValidationError, ParameterError


bp = Blueprint('minipro', __name__, url_prefix='/minipro')


@bp.route("/users", methods=['GET', 'POST'])
def users():
    pass

 
class PostView(MethodView):
    def get(self, post_id):
        limit = request.args.get('limit')
        res = []
        if post_id:
            post = Post.query.filter_by(id=post_id).first()
            resp = post.to_dict()
            resp['images'] = post.get_images()
            user = post.user
            print(user.nickname, user.avatar)
            resp['author'] = {
                'nickname': user.nickname,
                'avatar': user.avatar
            }
            location = post.location
            resp['location'] = json.loads(location) if location else None
            resp['styled'] = [{'tag': '', 'text': '内容1111111'}]  #  例如： #bug反馈#  content: bug反馈
            return resp

        query = Post.query.order_by(Post.id.desc())
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
            r['styled'] = [{'tag': '', 'text': '内容1111111'}]
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
