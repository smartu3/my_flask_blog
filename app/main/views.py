#-*- coding:utf-8 -*- 

from . import main
from flask import render_template,request,current_app
from .. import db
from ..models import User
from .forms import EditProfileForm,GravatorForm
from flask_login import current_user,login_required
from .. import gravators
import os

@main.route('/')
def index():
	return render_template('index.html')

@main.route('/user-gravator/<username>',methods=['GET','POST'])
def user(username):
	user=User.query.filter_by(username=username).first()
	form = GravatorForm()
	if user is None:
		abort(404)
	file_url=current_user.gravator_url
	if request.method == 'POST' and 'gravator' in request.files:
		if file_url is not None:
			user_folder=os.path.join(current_app.config['UPLOADED_GRAVATORS_DEST'],current_user.username)
			files_list = os.listdir(user_folder)
			for photo in files_list:
				file_path = gravators.path(photo)
				os.remove(os.path.join(user_folder,photo))
		filename = gravators.save(request.files['gravator'],current_user.username)
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