#-*- coding:utf-8 -*-

from flask import render_template,redirect,request,url_for,flash,session,g
from flask_login import login_user,login_required,current_user,logout_user,fresh_login_required
from . import auth 
from .forms import LoginForm,RegisterForm,ModifyPasForm,ResetPasswordForm,ConfirmForm,ModifyEmailForm
from ..models import User,Role,load_user
from  .. import db
from ..email import send_email

@auth.before_app_request
def before_request():
	g.user = current_user
	if current_user.is_authenticated and not current_user.confirmed \
	and request.endpoint[:5] !='auth.' and request.endpoint !='static':
		return redirect(url_for('auth.unconfirmed'))

@auth.after_app_request
def after_request(response):
	if current_user.is_authenticated:
		current_user.ping()
	return response


@auth.route('/login',methods=['GET','POST'])
def login():
	r_form = RegisterForm()
	l_form = LoginForm()
	if g.user is not None and g.user.is_authenticated:
		login_user(load_user(g.user.id),True,False,False)
		return redirect(url_for('main.index'))
	if r_form.register_submit.data and r_form.validate_on_submit():
		user=User(email=r_form.email.data,username=r_form.username.data,password=r_form.password.data)
		db.session.add(user)
		db.session.commit()
		login_user(user)
		flash(u'注册成功','success')
		token = user.generate_confirmation_token()
		send_email(user.email,'Confirmation','auth/email/confirm',user=user,token=token)
		return redirect(url_for('auth.login'))
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
	flash(u'你已退出登录','success')
	return redirect(url_for('main.index'))

@auth.route('/confirm/<token>')
@login_required
def confirm(token):
	if current_user.confirmed:
		return redirect(url_for('main.index'))
	if current_user.confirm(token):
		flash(u'你已成功确认。','success')
	else:
		flash('确认链接无效或过期。','warning')
	return redirect(url_for('main.index'))

@auth.route('/unconfirmed')
def unconfirmed():
	if current_user.is_anonymous or current_user.confirmed:
		return redirect(url_for('main.index'))
	return render_template('auth/unconfirmed.html')

@auth.route('/resend_confirmation')
@login_required
def resend_confirmation():
	token = current_user.generate_confirmation_token()
	send_email(current_user.email,'Confirm your email','auth/email/confirm',user=current_user,token=token)
	flash(u'一封新的确认邮件已经发往了你的注册邮箱','info')
	return redirect(url_for('main.index'))

@auth.route('/modify',methods=['GET','POST'])
@login_required
def modify():
	form = ModifyPasForm()
	user=User.query.filter_by(username=current_user.username).first()
	if form.validate_on_submit() and user.verify_password(form.oldpassword.data):
		user.password=form.password.data
		db.session.add(user)
		flash(u'成功修改密码','success')
		return redirect(url_for('main.index'))
	return render_template('auth/modify_password.html',form=form)

@auth.route('/reset1',methods=['GET','POST'])
def reset1():
	form = ConfirmForm()
	if form.validate_on_submit():
		if User.query.filter_by(email=form.email.data).first():
			user = User.query.filter_by(email=form.email.data).first()
			token = user.generate_confirmation_token()
			send_email(form.email.data,"Confirm your email",'auth/email/resetconfirm',user=user,token=token)
			flash("一封新的确认邮件已经发往你的邮箱。")
			return redirect(url_for("main.index"))
		else:
			flash(u"无效的邮箱地址。")
	return render_template("auth/reset1.html",form=form)

@auth.route('/reset2/<token>',methods=['GET','POST'])
def reset2(token):
	form = ResetPasswordForm()
	if form.validate_on_submit():
		user=User.query.filter_by(email=form.email.data).first()
		if user.confirm(token):
			user.password=form.password.data
			flash(u"成功修改密码，现在可以登录。")
			return redirect(url_for("auth.login"))
		else:
			flash(u"请重新确认你的重置链接。")
	return render_template("auth/reset2.html",form=form)

@auth.route('/resetmaill',methods=['GET','POST'])
def resetmail1():
	form = ConfirmForm()
	if form.validate_on_submit():
		if current_user.email == form.email.data:
			token=current_user.generate_confirmation_token()
			send_email(form.email.data,"Confirm your email.","auth/email/resetconfirmemail",user=current_user,token=token)
			flash(u"一封新的确认邮件已经发往了你的注册邮箱。")
			return redirect(url_for("main.index"))
		else:
			flash(u"无效的邮箱地址。")
	return render_template("auth/reset1.html",form=form)

@auth.route('/resetemail2/<token>',methods=['GET','POST'])
def resetemail2(token):
	form =ResetEmailForm()
	if form.validate_on_submit():
		if User.query.filter_by(email=form.email.data).first():
			flash(u"该邮箱已经被注册。")
		else:
			user=User.query.filter_by(email=form.oldemail.data).first()
			if user.confirm(token):
				user.email=form.email.data
				flash(u"你已经重置了你的邮箱地址。")
				return redirect(url_for("main.index"))
			else:
				flash(u"请确认重置链接是否有效或过期。")
	return render_template("auth/resetemail.html",form=form)