#-*- coding:utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,BooleanField,SubmitField
from wtforms.validators import Required,Length,Email

class LoginForm(FlaskForm):
	email = StringField(u'邮箱',validators=[Required(),Length(1,64),Email(u'请输入有效地址,如 \
		example@gmail.com.')])
	password=PasswordField(u'密码',validators=[Required(u'请输入密码')])
	remember_me = BooleanField(u'记住我')
	login_submit=SubmitField(u'登录')

class RegisterForm(FlaskForm):
	email = StringField(u'邮箱',validators=[Required(),Length(1,64),Email()])
	username=StringField(u'用户名',validators=[Required(),Length(1,64)])
	register_submit=SubmitField(u'注册')