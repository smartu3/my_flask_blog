#-*- coding:utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,BooleanField,SubmitField
from wtforms.validators import Required,Length,Email,EqualTo
from wtforms import ValidationError
from ..models import User

class LoginForm(FlaskForm):
	email = StringField(u'邮箱',validators=[Required(),Length(1,64),Email(u'请输入有效地址,如 \
		example@gmail.com.')])
	password=PasswordField(u'密码',validators=[Required(u'请输入密码')])
	remember_me = BooleanField(u'记住我')
	login_submit=SubmitField(u'登录')

class RegisterForm(FlaskForm):
	email = StringField(u'邮箱',validators=[Required(),Length(1,64),Email()])
	username=StringField(u'用户名',validators=[Required(),Length(1,64)])
	password = PasswordField(u'密码',validators=[Required(),Length(6,64),EqualTo('password2',message=u'两次密码需要一致')])
	password2=PasswordField(u'确认密码',validators=[Required(),Length(6,64)])
	register_submit=SubmitField(u'注册')

	def validate_email(self,field):
		if User.query.filter_by(email=field.data).first():
			raise ValidationError(u'该账户已经被注册')

	def validate_username(self,field):
		if User.query.filter_by(username=field.data).first():
			raise ValidationError(u'该用户名已经被注册')

class ModifyPasForm(FlaskForm):
	oldpassword=PasswordField(u'旧密码',validators=[Required(),Length(6,64)])
	password = PasswordField(u'新密码',validators=[Required(),Length(6,64),EqualTo('password2',message=u'两次密码需要一致')])
	password2=PasswordField(u'确认密码',validators=[Required(),Length(6,64)])
	submit=SubmitField(u'提交')

class ConfirmForm(FlaskForm):
	email=StringField(u"邮箱地址",validators=[Required(),Email()])
	submit=SubmitField(u'确认')

class ResetPasswordForm(FlaskForm):
	email=StringField(u'你的邮件地址',validators=[Required(),Length(1,64),Email()])
	password=PasswordField(u'密码',validators=[Required(),Length(6,64),EqualTo('password2',message='Passwords'
	'must match')])
	password2=PasswordField(u'确认密码',validators=[Required()])
	submit=SubmitField(u'提交')

class ModifyEmailForm(FlaskForm):
	oldemail=email=StringField(u"旧邮箱地址",validators=[Required(),Email()])
	email=StringField(u"新邮箱地址",validators=[Required(),Email(),EqualTo('email2',message='Email must match')])
	email2=StringField(u"确认你的邮箱地址。",validators=[Required(),Email()])
	submit=SubmitField(u'提交')