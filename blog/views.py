from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import Post, User
from . import db

views = Blueprint('views', __name__)


@views.route('/')
@views.route('/home')
def home():
    posts = Post.query.all()
    return render_template('home.html', user=current_user, posts=posts)


@views.route('/about')
def about():
    return render_template('about.html')


@views.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        flash('Message sent', category='success')
        return redirect(url_for('views.home'))
    return render_template('contact.html')


@views.route('/creatPosts', methods=['GET', 'POST'])
@login_required
def createPosts():
    if request.method == 'POST':
        content = request.form.get('content')
        if not content:
            flash('Post is empty!', category='error')
        else:
            post = Post(content=content, author=current_user.id)
            db.session.add(post)
            db.session.commit()
            flash('Post created!', category='success')
            return redirect(url_for('views.home'))
            
    return render_template('createPost.html', name=current_user.username)

@views.route('/delete/<id>')
def delete_post(id):
    post = Post.query.filter_by(id=id).first()
    if not post:
        flash('Post does not exist', category='error')
    elif current_user.id != post.id:
        flash('You do not have permission to delete this post', category='error')
    else:
        db.session.delete(post)
        db.session.commit()
        flash('Post deleted!', category='success')
    return redirect(url_for('views.home'))

@views.route('/edit/<id>', methods=['GET', 'POST'])
def edit_post(id):
    post = Post.query.get(id)
    if not post:
        flash('Post does not exist', category='error')
    elif current_user.id != post.id:
        flash('You do not have permission to edit this post', category='error')
    else:
        if request.method == 'POST':
            post.content = request.form.get('content')
            if not post.content:
                flash('Post is empty!', category='error')
            else:
                db.session.add(post)
                db.session.commit()
                flash('Post edited!', category='success')
                return redirect(url_for('views.home'))
    post.content = post.content
    return render_template('edit.html', post=post)


@views.route('/post/<username>')
@login_required
def post(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('User does not exist', category='error')
        redirect(url_for('views.home'))
    else:
        posts = Post.query.filter_by(author=user.id).all()
        return render_template('post.html', posts=posts, username=username, user=current_user)

@views.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@views.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500
