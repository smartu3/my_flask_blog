#-*- coding:utf-8 -*- 

from . import main
from flask import render_template,request,current_app,redirect,url_for,flash,abort
from .. import db
from ..models import User,Role,Post,Permission,Comment
from .forms import EditProfileForm,GravatorForm,PostForm,CommentForm
from flask_login import current_user,login_required
from .. import gravators
from ..decorators import admin_required,permission_required
import os

@main.route('/')
def index():
	return render_template('index.html')

@main.route('/all-posts')
def posts():
	page = request.args.get('page',1,type=int)
	pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
		page,per_page = 10,error_out=False)
	posts = pagination.items
	return render_template('allposts.html',posts=posts,pagination=pagination)

@main.route('/followed-posts')
@login_required
def show_followed():
	page = request.args.get('page',1,type=int)
	if current_user.is_authenticated:
		query = current_user.followed_posts
	pagination = query.order_by(Post.timestamp.desc()).paginate(
		page,per_page=20,error_out=False)
	posts = pagination.items
	return render_template('followedposts.html',posts=posts,pagination=pagination)

@main.route('/mypost',methods=['GET','POST'])
@login_required
def mypost():
	user = User.query.filter_by(username=current_user.username).first()
	if user is None:
		abort(404)
	form = PostForm()
	page = request.args.get('page',1,type=int)
	pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
		page,per_page = 15,error_out = False)
	posts = pagination.items
	if form.validate_on_submit():
		post=Post(title=form.title.data,body=form.body.data,author=user)
		db.session.add(post)
		return redirect(url_for('main.mypost'))
	return render_template('mypost.html',pagination=pagination,posts=posts,form=form)

@main.route('/delete_post/<int:id>')
def delete_post(id):
	post=Post.query.get_or_404(id)
	user=post.author
	if current_user == user or current_user.is_administrator():
		db.session.delete(post)
		flash(u"成功删除。",'success')
		return redirect(url_for("main.posts"))
	else:
		abort(404)
		return redirect(url_for(".index"))

@main.route('/post/<int:id>',methods=['GET','POST'])
def post(id):
	post=Post.query.get_or_404(id)
	post.clicknum += 1
	form=CommentForm()
	if form.validate_on_submit():
		comment=Comment(body=form.body.data,post=post,author=current_user._get_current_object())
		db.session.add(comment)
		flash(u"评论成功","success")
		return redirect(url_for('main.post',id=post.id,page=-1))
	page=request.args.get("page",1,type=int)
	if page == -1:
		page= (post.comments.count() -1 )/ int(15) +1
	pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(page,per_page=\
		int(15),error_out = False)
	comments=pagination.items
	return render_template('post.html',posts=[post],form=form,comments=comments,pagination=pagination)

@main.route('/popular-post')
def popular_post():
	page = request.args.get("page",1,type=int)
	pagination = Post.query.order_by(Post.clicknum.desc()).paginate(page,per_page = \
		int(15),error_out = False)
	posts = pagination.items
	return render_template('popular-posts.html',pagination=pagination,posts=posts)

@main.route('/edit/<int:id>',methods=['GET','POST'])
@login_required
def edit(id):
	post=Post.query.get_or_404(id)
	if current_user != post.author and not current_user.can(Permission.ADMINISTER):
		abort(403)
	form = PostForm()
	if form.validate_on_submit():
		post.body=form.body.data
		post.title=form.title.data
		db.session.add(post)
		flash(u"已更新","success")
		return redirect(url_for("main.post",id=post.id))
	form.body.data=post.body
	form.title.data=post.title
	return render_template("edit_post.html",form=form,user=post.author,id=id)

@main.route('/delete-warning/<int:id>')
def warning(id):
	if current_user != Post.query.get_or_404(id).author and not current_user.can(Permission.ADMINISTER):
		abort(403)
	flash(u"确定删除吗？删除将不可恢复。","danger")
	return render_template("warning.html",id=id)

@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate():
	page=request.args.get("page",1,type=int)
	pagination=Comment.query.order_by(Comment.timestamp.desc()).paginate(page,per_page=int(15),
		error_out=False)
	comments=pagination.items
	return render_template('moderate.html',comments=comments,pagination=pagination,page=page)

@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disable(id):
	comment=Comment.query.get_or_404(id)
	comment.disabled=True
	db.session.add(comment)
	page=request.args.get('page',1,type=int)
	return redirect(url_for('main.moderate',page=page))

@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_enable(id):
	comment=Comment.query.get_or_404(id)
	comment.disabled=False
	db.session.add(comment)
	page=request.args.get("page",1,type=int)
	return redirect(url_for('main.moderate',page=page))


@main.route('/user-gravator/<username>',methods=['GET','POST'])
@login_required
def user(username):
	if current_user.username != username:
		abort(404)
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

@main.route('/friends/<username>')
def friends(username):
	user=User.query.filter_by(username=username).first()
	if user is None:
		flash(u"无效用户.")
		return redirect(url_for('main.index'))
	follows=user.Friend_lists()
	return render_template("friends.html",user=user,title="Friends",follows=follows)

@main.route('/<username>/user/')
@login_required
def checkuser(username):
	user=User.query.filter_by(username=username).first()
	if user is None:
		abort(404)
	page=request.args.get('page',1,type = int)
	pagination=Post.query.filter_by(author=user).order_by(Post.timestamp.desc()).paginate(page,per_page=int(15),
		error_out=False)
	posts=pagination.items
	return render_template('checkuser.html',user=user,posts=posts,pagination=pagination,friend_num=len(user.Friend_lists()))

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
		return redirect(url_for('main.user',username=current_user.username))
	if current_user.is_authenticated:
		form.name.data = current_user.name
		form.location.data = current_user.location
		form.sign.data = current_user.sign
	return render_template('profile.html',form=form)

@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
	user=User.query.filter_by(username=username).first()
	if user is None:
		flash(u"无效用户.",'warning')
		return redirect(url_for("main.index"))
	if current_user.is_following(user):
		flash(u"你已经关注了该用户",'info')
		return redirect(url_for("main.checkuser",username=username))
	current_user.follow(user)
	flash(u"成功关注 %s中." % username,'success')
	return redirect(url_for("main.checkuser",username=username))

@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
	user=User.query.filter_by(username=username).first()
	if user is None:
		flash(u"无效用户.",'warning')
		return redirect(url_for("main.index"))
	if not current_user.is_following(user):
		flash(u"你已经取消关注了该用户",'info')
		return redirect(url_for("main.checkuser",username=username))
	current_user.unfollow(user)
	flash(u"已成功取消关注 %s." % username,'success')
	return redirect(url_for("main.checkuser",username=username))

@main.route('/followers/<username>')
def followers(username):
	user=User.query.filter_by(username=username).first()
	if user is None:
		flash(u"无效用户.",'warning')
		return redirect(url_for("main.index"))
	page=request.args.get("page",1,type=int)
	pagination=user.followers.paginate(page,per_page=int(15),error_out=False)
	follows=[{'user':item.follower,'timestamp':item.timestamp} for item in pagination.items]
	return render_template('followers.html',user=user,title=u"的粉丝",endpoint="main.followers", \
		pagination=pagination,follows=follows)

@main.route('/followed/<username>')
def followed(username):
	user=User.query.filter_by(username=username).first()
	if user is None:
		flash(u"无效用户.",'warning')
		return redirect(url_for("main.index"))
	page=request.args.get("page",1,type=int)
	pagination=user.followed.paginate(page,per_page=int(15),error_out=False)
	follows=[{'user':item.followed,'timestamp':item.timestamp} for item in pagination.items]
	return render_template('followers.html',user=user,title=u"的关注用户",endpoint="main.followed", \
		pagination=pagination,follows=follows)