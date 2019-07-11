from flask import Blueprint, request
from flask.views import MethodView

from web.core import db
from web.models.minipro_bbs import Post, PostImage
from web.forms.minipro_bbs import PostForm
from web.exceptions import BaseException, FormValidationError, ParameterError


bp = Blueprint('minipro', __name__, url_prefix='/minipro')


class PostView(MethodView):
    def get(self, post_id):
        res = []
        if post_id:
            post = Post.query.filter_by(id=post_id).first()
            res =  post.to_dict()
            res['images'] = post.get_images()
            return res 

        posts = Post.query.all()
        for post in posts:
            images = post.get_images()
            r = post.to_dict()
            r['images'] = images
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
            db.session.add(post_obj)
            db.session.flush()
            images = req_data.get('images', [])
            
            for img in images:
                img_url = img.get('image_url')
                post_image = PostImage(image_ur=img_url, post_id=post_obj.id)
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
