# -*-coding:utf-8 -*-

import unittest
from app.models import User
from manage import create_app
from app import db


class test_user_model(unittest.TestCase):
	def setUp(self):
		self.app = create_app('testing')
		self.app_context=self.app.app_context()
		self.app_context.push()
		db.create_all()

	def tearDown(self):
		db.session.remove()
		db.drop_all()
		self.app_context.pop()

	def test_password_setter(self):
		u = User(password='cat')
		self.assertTrue(u.password_hash is not None)

	def test_no_password_getter(self):
		u=User(password='cat')
		with self.assertRaises(AttributeError):
			u.password

	def test_password_verification(self):
		u=User(password='cat')
		self.assertTrue(u.verify_password('cat'))
		self.assertFalse(u.verify_password('dog'))

	def test_password_salts_are_random(self):
		u=User(password='cat')
		u2=User(password='cat')
		self.assertTrue(u.password_hash !=u2.password_hash)

	def test_generate_confirm_token(self):
		u=User()
		self.assertTrue(u.confirmed is None)
		self.assertTrue(u.generate_confirmation_token is not None)

	def test_confirm(self):
		u=User()
		token = u.generate_confirmation_token()
		self.assertTrue(u.confirm(token))
		self.assertTrue(u.confirmed)