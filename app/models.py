#-*- coding:utf-8 -*-
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin,logout_user,AnonymousUserMixin
from flask import current_app,flash,redirect,url_for
from . import db
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from datetime import datetime
from  . import login_manager
from markdown import markdown
import bleach

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

class Follow(db.Model):
	__tablename__='follows'
	follower_id=db.Column(db.Integer,db.ForeignKey('users.id'),primary_key=True)
	followed_id=db.Column(db.Integer,db.ForeignKey('users.id'),primary_key=True)
	timestamp=db.Column(db.DateTime,default=datetime.utcnow)


	def __repr__(self):
		return "<Follower:%r,Followed:%r>" % (self.follower.username,self.followed.username)

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
	posts = db.relationship('Post',backref = 'author',lazy = 'dynamic')
	comments = db.relationship('Comment',backref="author",lazy="dynamic")

	followed=db.relationship('Follow',foreign_keys=[Follow.follower_id],backref=db.backref('follower',lazy='joined'),lazy='dynamic',
							cascade='all,delete-orphan')
	followers=db.relationship('Follow',foreign_keys=[Follow.followed_id],backref=db.backref('followed',lazy='joined'),lazy='dynamic',
							cascade='all,delete-orphan')


	def follow(self,user):
		if not self.is_following(user):
			f = Follow(follower=self,followed=user)
			db.session.add(f)
	def unfollow(self,user):
		f = self.followed.filter_by(followed_id=user.id).first()
		if f:
			db.session.delete(f)

	def is_following(self,user):
		return self.followed.filter_by(followed_id=user.id).first() is not None

	def is_followed_by(self,user):
		return self.followers.filter_by(follower_id=user.id).first() is not None

	def Friend_lists(self):
		follow_list = self.followed.all()
		Friend_lists=[]
		for follow in follow_list:
			if follow.followed.is_following(self):
				Friend_lists.append(follow.followed)
		return Friend_lists

	@property
	def followed_posts(self):
		return Post.query.join(Follow,Follow.followed_id==Post.author_id)\
			.filter(Follow.follower_id==self.id)

	def ping(self):
		self.last_seen = datetime.utcnow()
		db.session.add(self)

	def __init__(self,**kwargs):
		super(User,self).__init__(**kwargs)
		if self.role is None:
			if self.email ==current_app.config['BLOG_ADMIN']:
				self.role= Role.query.filter_by(permission=0xff).first()
				self.confirmed = True
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

class Post(db.Model):

	__tablename__ = 'posts'
	id = db.Column(db.Integer,primary_key = True)
	title = db.Column(db.String(64))
	body = db.Column(db.Text)
	body_html = db.Column(db.Text)
	timestamp = db.Column(db.DateTime, index=True,default = datetime.utcnow)
	author_id = db.Column(db.Integer,db.ForeignKey('users.id'))
	comments = db.relationship('Comment',backref='post',lazy='dynamic')


	def __repr__(self):
		return '<Post %r>' % self.title

	@staticmethod
	def on_changed_body(target,value,oldvalue,initiator):
		allowed_tags = ['a','abbr','acronym','b','blockquote','code', \
			'em','i','li','ol','pre','strong','ul','h1','h2','h3','p']
		target.body_html=bleach.linkify(bleach.clean( \
			markdown(value,output_format='html'), \
			tags=allowed_tags,strip=True))

db.event.listen(Post.body,'set',Post.on_changed_body)



class Comment(db.Model):
	__tablename__='comments'
	id=db.Column(db.Integer,primary_key=True)
	body=db.Column(db.Text)
	body_html=db.Column(db.Text)
	timestamp=db.Column(db.DateTime,index=True,default=datetime.utcnow)
	disabled=db.Column(db.Boolean)
	author_id=db.Column(db.Integer,db.ForeignKey('users.id'))
	post_id=db.Column(db.Integer,db.ForeignKey('posts.id'))


	def __repr__(self):
		return '<Comment %d>' % self.id

	@staticmethod
	def on_changed_body(target,value,oldvalue,initiator):
		allowed_tags=['a','abbr','acronym','b','code','em','i','strong']
		target.body_html=bleach.linkify(bleach.clean(markdown(value,output_format='html'),tags=allowed_tags,strip=True))

	def to_json(self):
		json_post_comments={
			'url':url_for('api.get_post_comments',id.self.post_id,_external=True),
			'body':self.body,
			'body_html':self.body_html,
			'timestamp':self.timestamp,
			'author':url_for('api.get_user',id=self.author_id,_external=True),
			'post':url_for('api.get_post',id=self.post_id,_external=True)
			}
		return json_post_comments

	@staticmethod
	def from_json(json_comment):
		body=json_comment.get('body')
		if body is None or body =='':
			raise ValidationError("Comment does not have a body.")
		return Comment(body=body)

db.event.listen(Comment.body,'set',Comment.on_changed_body)





from . import login_manager
@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

@login_manager.needs_refresh_handler
def refresh_login():
	logout_user()
	flash(u'需要重新登录','warning')
	return redirect(url_for('auth.login'))