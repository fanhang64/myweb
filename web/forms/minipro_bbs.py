from wtforms import Form
from wtforms.fields import IntegerField, StringField
from wtforms.validators import DataRequired, Length


class PostForm(Form):
    title = StringField("标题", validators=[DataRequired()])
    content = StringField("内容", validators=[DataRequired()])
    author_id = StringField("作者", validators=[DataRequired()])


class PostFavorForm(Form):
    from_user_id = IntegerField('点赞人', validators=[DataRequired()])
    to_user_id = IntegerField('被点赞人', validators=[DataRequired()])
    post_id = IntegerField('帖子id', validators=[DataRequired()])


class PostCommentForm(Form):
    uid = IntegerField('用户id', validators=[DataRequired()])    
    post_id = IntegerField('帖子id', validators=[DataRequired()])
    content = IntegerField('评论内容', validators=[DataRequired()])