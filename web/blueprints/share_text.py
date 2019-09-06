from flask import Blueprint, render_template, request
from flask.views import MethodView

from web.utils.share_text import gen_share_code
from web.models.share_text import ShareCode
from web.exceptions import CustomBaseException
from web.core import db
from web.config import Config


bp = Blueprint('share', __name__)


class ShareTextView(MethodView):
    def get(self):
        code = request.args.get('code')

        if code:
            share_code = ShareCode.query.filter_by(code=code).first()
            if share_code:
                share_url = Config.ShareTextUrl + "/share/?code="+code
                return render_template('show_share_text.html', **{'share_url': share_url, 'text': share_code.text})
            else:
                return render_template('404.html')
        else:
            return render_template('index.html')

    def post(self):
        req_data = request.json
        if not req_data:
            raise CustomBaseException('参数缺失')

        content = req_data.get('text')
        share_code_list = ShareCode.query\
            .with_entities(ShareCode.code).all()
        share_code_list = [x[0] for x in share_code_list]

        while True:
            code = gen_share_code()
            if code not in share_code_list:
                break
        share_code = ShareCode()
        share_code.code = code
        share_code.text = req_data.get('content')
        db.session.add(share_code)
        db.session.commit()

        share_url = Config.ShareTextUrl + "/share/?code="+code
        return {'data':share_url}


share_text_view = ShareTextView.as_view('share_text')
bp.add_url_rule('/share/', view_func=share_text_view, methods=['GET', 'POST'])
