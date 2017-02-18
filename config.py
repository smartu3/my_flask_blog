#-*- coding:utf-8 -*-

import os 
basedir=os.path.abspath(os.path.dirname(__file__))

class Config:
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'very veyr hard to guess'
	SQLALCHEMY_COMMIT_ON_TEARDOWN = True
	BLOG_MAIL_SUBJECT_PREFIX='[Welcome]'
	BLOG_MAIL_SENDER = '123389602@qq.com'
	BLOG_ADMIN= os.environ.get('BLOG_ADMIN') or 'zhze93@qq.com' 
	SQLALCHEMY_TRACK_MODIFICATIONS = True
	UPLOADED_GRAVATORS_DEST = os.getcwd() + '\gravators'
	@staticmethod
	def init_app(app):
		pass

class DevelopmentConfig(Config):
	DEBUG = True
	MAIL_SENDER = '123389602@qq.com'
	MAIL_SERVER = 'smtp.qq.com'
	MAIL_PORT = 587
	MAIL_USE_TLS = True
	MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
	MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
	SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
		'sqlite:///' + os.path.join(basedir,'data-dev.sqlite')

class TestingConfig(Config):
	TESTING = True
	SQLALCHEMY_DATABASE_URI=os.environ.get('TEST_DATABASE_URL') or \
		'sqlite:///' + os.path.join(basedir,'data-test.sqlite')

class ProductionConfig(Config):
	SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://<username>:<password>@localhost/pump_pro'

config={
	'development': DevelopmentConfig,
	'testing':TestingConfig,
	'production':ProductionConfig,

	'default':DevelopmentConfig
	}