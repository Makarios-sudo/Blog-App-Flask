
from app.models import User, Post
from app import app, db, bcrypt
from flask import render_template, url_for, flash, redirect, request, abort
from app.forms import RegisterationForm, LoginForm, UpdateAccountForm, GistForm
from flask_login import login_user, current_user, logout_user, login_required
import secrets, os
from PIL import Image


# setting homepage route
@app.route("/")
def home():
    page = request.args.get("page", 1, type=int)
    gists = Post.query.order_by(Post.date_posted.desc()).paginate(page = page, per_page=5)
    return render_template("home.html", gists=gists)

@app.route("/about")
def about():
    return render_template("about.html", title="About Page")


@app.route("/register", methods=('GET', 'POST'))
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    form = RegisterationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(username = form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash("Account Created successfully", "success")
        return redirect(url_for("login") )
    return render_template("register.html", form=form, title="Register")


@app.route("/login", methods=("GET", "POST"))
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    form = LoginForm()
    if form.validate_on_submit():
       user = User.query.filter_by(email=form.email.data).first()
       if user and bcrypt.check_password_hash(user.password, form.password.data):
           login_user(user, remember=form.remember.data)
           next_page = request.args.get("next")
           return redirect(next_page) if next_page else redirect(url_for("home"))
       else:
        flash(f"Login Failed, Please provide the correct Email and Password")
    return render_template("login.html", form=form, title="Login")


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn =random_hex + f_ext
    picture_path = os.path.join(app.root_path, "static/profile_pics", picture_fn)
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn


@app.route("/account", methods=("GET", "POST"))
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash("Your account has been updated")
        return redirect(url_for("account"))
    elif request.method  == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template("account.html", title="Account", image_file=image_file, form=form)


@app.route("/gists/new", methods=("GET", "POST"))
@login_required
def new_gist():
    form = GistForm()
    if form.validate_on_submit():
        gist = Post(title = form.title.data, content = form.content.data, author = current_user )
        db.session.add(gist)
        db.session.commit()
        flash("Your created post was successful")
        return redirect(url_for("home"))
    return render_template("createGist.html", form=form, form_header="New Gist")


@app.route("/gist/<int:gist_id>")
def gist(gist_id):
    gist = Post.query.get_or_404(gist_id)
    return render_template("gist.html", gist=gist)


@app.route("/gist/<int:gist_id>/update", methods=("GET", "POST"))
@login_required
def update_Gist(gist_id):
    gist = Post.query.get_or_404(gist_id)
    if gist.author != current_user:
        abort(403)
    form = GistForm()
    if form.validate_on_submit():
        gist.title = form.title.data
        gist.content = form.content.data
        db.session.commit()
        flash("Your gist is successfully updated")
        return redirect(url_for("gist", gist_id = gist.id))
    elif request.method == "GET":
        form.title.data = gist.title
        form.content.data = gist.content
    return render_template("createGist.html", form=form, form_header="Update Gist")


@app.route("/gist/<int:gist_id>/delete", methods=["POST"])
@login_required
def delete_Gist(gist_id):
    gist = Post.query.get_or_404(gist_id)
    if gist.author != current_user:
        abort(403)
    db.session.delete(gist)
    db.session.commit()
    flash("Your gist is deleted")
    return redirect(url_for("home"))


@app.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get("page", 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    gists = Post.query.filter_by(author=user)\
            .order_by(Post.date_posted.desc())\
            .paginate(page = page, per_page=5)
    return render_template("user_post.html", gists=gists, user=user)
