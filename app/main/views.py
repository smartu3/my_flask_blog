#-*- coding:utf-8 -*- 

from . import main
from flask import render_template,request
from .. import db
from ..models import User
from .forms import EditProfileForm,GravatorForm
from flask_login import current_user,login_required
from .. import gravators


@main.route('/')
def index():
	return render_template('index.html')

@main.route('/user/<username>',methods=['GET','POST'])
def user(username):
	user=User.query.filter_by(username=username).first()
	form = GravatorForm()
	print (current_user.username == user.username)
	if user is None:
		abort(404)
	file_url=current_user.gravator_url
	if request.method == 'POST' and 'gravator' in request.files:
		filename = gravators.save(request.files['gravator'])
		file_url = gravators.url(filename)
		current_user.gravator_url=file_url
		return render_template('user.html',user=user,form=form,file_url=file_url)
	return render_template('user.html',user=user,form=form,file_url=file_url)

@main.route('/user/profile-eidt/<username>',methods=['GET','POST'])
@login_required
def profiel_edit(username):
	form = EditProfileForm()
	user=User.query.filter_by(username=username).first()
	if current_user.username != user.username:
		abort(404)
	if form.validate_on_submit():
		current_user.name = form.name.data
		current_user.location = form.location.data
		current_user.sign = form.sign.data
		db.session.add(current_user)
		return render_template('profile.html',form=form)
	if current_user.is_authenticated:
		form.name.data = current_user.name
		form.location.data = current_user.location
		form.sign.data = current_user.sign
	return render_template('profile.html',form=form)