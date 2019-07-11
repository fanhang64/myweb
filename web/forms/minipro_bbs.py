from wtforms import Form
from wtforms.fields import IntegerField, StringField
from wtforms.validators import DataRequired, Length


class PostForm(Form):
    title = StringField("标题", validators=[DataRequired()])
    content = StringField("内容", validators=[DataRequired()])
    author_id = StringField("作者", validators=[DataRequired()])

