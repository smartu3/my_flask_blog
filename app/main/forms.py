#-*- coding:utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,BooleanField,SubmitField,TextAreaField
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.validators import Required,Length,Email,EqualTo
from wtforms import ValidationError
from ..models import User
from .. import gravators
from flask_pagedown.fields import PageDownField



class EditProfileForm(FlaskForm):
	name = StringField(u'昵称',validators=[Length(0,64)])
	location=StringField(u'位置',validators=[Length(0,64)])
	sign=TextAreaField(u'签名',validators=[Length(0,64)])
	submit=SubmitField(u'提交')

class GravatorForm(FlaskForm):
	gravator = FileField(u'图片上传', validators=[FileAllowed(gravators, u'只能上传图片！'),Required()])
	submit=SubmitField(u'提交')

class PostForm(FlaskForm):
	title = StringField(u"标题", validators=[Required()])
	body = PageDownField(u'正文',validators=[Required()])
	submit = SubmitField(u'发布')

class CommentForm(FlaskForm):
	body=PageDownField(u'请输入评论',validators=[Required()])
	submit=SubmitField(u'提交')