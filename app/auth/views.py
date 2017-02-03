#-*- coding:utf-8 -*-

from flask import render_template,redirect,request,url_for,flash,session,g
from flask_login import login_user,login_required,current_user,logout_user
from . import auth 
from .forms import LoginForm,RegisterForm
from ..models import User,Role,load_user
from .forms import LoginForm,RegisterForm

@auth.before_request
def before_request():
	g.user = current_user




@auth.route('/login',methods=['GET','POST'])
def login():
	if g.user is not None and g.user.is_authenticated:
		login_user(load_user(g.user.id),True,False,False)
		return redirect(url_for('main.index'))
	r_form = RegisterForm()
	l_form = LoginForm()
	if r_form.register_submit.data and r_form.validate_on_submit():
		pass
	if l_form.login_submit.data and l_form.validate_on_submit():
		user = User.query.filter_by(email=l_form.email.data).first()
		if user is not None and user.verify_password(l_form.password.data):
			login_user(user,l_form.remember_me.data)
			return redirect(request.args.get('next') or url_for('main.index'))
		flash(u'无效的用户名或密码。','danger')
	return render_template('auth/login.html',r_form=r_form,l_form=l_form)

@auth.route('/logout')
@login_required
def logout():
	logout_user()
	flash(u'你已经退出登录','success')
	return redirect(url_for('main.index'))