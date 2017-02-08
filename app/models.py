#-*- coding:utf-8 -*-
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin,logout_user,AnonymousUserMixin
from flask import current_app,flash,redirect,url_for
from . import db
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from datetime import datetime
from  . import login_manager

class Permission:
	FOLLOW = 0x01
	COMMENT = 0x02
	WRITE_ARTICLES=0x04
	MODERATE_COMMENTS = 0x08
	ADMINISTER = 0x80

class AnonymousUser(AnonymousUserMixin):
	def can(self,permission):
		return False
	def is_administrator(self):
		return False
login_manager.anonymous_user=AnonymousUser

class Role(db.Model):
	__tablename__='roles'
	id = db.Column(db.Integer,primary_key = True)
	name = db.Column(db.String(64),unique = True)
	users=db.relationship('User',backref='role',lazy='dynamic')
	default=db.Column(db.Boolean,default=False,index=True)
	permission=db.Column(db.Integer)


	@staticmethod
	def insert_roles():
		roles={
			'User':(Permission.FOLLOW|Permission.COMMENT|Permission.WRITE_ARTICLES,True),
			'Moderator':(Permission.FOLLOW|Permission.COMMENT|Permission.WRITE_ARTICLES|Permission.MODERATE_COMMENTS,False),
			'Administrator':(0xff,False)
			}
		for r in roles:
			role = Role.query.filter_by(name=r).first()
			if role is None:
				role = Role(name=r)
			role.permission = roles[r][0]
			role.default = roles[r][1]
			db.session.add(role)
		db.session.commit()

	def __repr__(self):
		return '<Role %r>' % self.name


class User(UserMixin,db.Model):
	__tablename__='users'
	id=db.Column(db.Integer,primary_key=True)
	email = db.Column(db.String(64),unique=True,index=True)
	username=db.Column(db.String(64),unique=True,index=True)
	role_id=db.Column(db.Integer,db.ForeignKey('roles.id'))
	password_hash=db.Column(db.String(64))
	confirmed = db.Column(db.Boolean,default = False)
	name=db.Column(db.String(64))
	location=db.Column(db.String(64))
	sign=db.Column(db.Text())
	member_since = db.Column(db.DateTime(),default=datetime.utcnow)
	last_seen = db.Column(db.DateTime(),default = datetime.utcnow)
	gravator_url = db.Column(db.String(64))

	def ping(self):
		self.last_seen = datetime.utcnow()
		db.session.add(self)



	def __init__(self,**kwargs):
		super(User,self).__init__(**kwargs)
		if self.role is None:
			if self.email ==current_app.config['BLOG_ADMIN']:
				self.role= Role.query.filter_by(permission=0xff).first()
			if self.role is None:
				self.role = Role.query.filter_by(default=True).first()

	def can(self,permission):
		return self.role is not None and (self.role.permission & permission) == permission

	def is_administrator(self):
		return self.can(Permission.ADMINISTER)

	def generate_confirmation_token(self,expiration=3600):
		s = Serializer(current_app.config['SECRET_KEY'],expiration)
		return s.dumps({'confirm':self.id})

	def confirm(self,token):
		s = Serializer(current_app.config['SECRET_KEY'])
		try:
			data = s.loads(token)
		except:
			return False
		if data.get('confirm') != self.id :
			return False
		self.confirmed = True
		db.session.add(self)
		return True

	@property
	def password(self):
		raise AttributeError('Password is not visible.')
	@password.setter
	def password(self,password):
		self.password_hash=generate_password_hash(password)

	def verify_password(self,password):
		return check_password_hash(self.password_hash,password)

	def __repr__(self):
		return '<User %r>' % self.username

from . import login_manager
@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

@login_manager.needs_refresh_handler
def refresh_login():
	logout_user()
	flash(u'需要重新登录','warning')
	return redirect(url_for('auth.login'))