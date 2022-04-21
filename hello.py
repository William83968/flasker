from email.policy import default
from ssl import OP_SINGLE_DH_USE
from tabnanny import check
from flask import Flask, render_template, flash, request, jsonify, redirect, url_for, abort
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate 
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date
from wtforms.widgets import TextArea

# Create a flask instance
app = Flask(__name__)
# Add Database
# Old sqlalchemy database
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:liu695395@localhost/our_users'
# Secret Key!
app.config['SECRET_KEY']="Dastor Bilgan"
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Create a Blog Post
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default=datetime.now)
    slug = db.Column(db.String(255))

# Create a Posts Form
class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    author = StringField("Author", validators=[DataRequired()])
    content = StringField("Content", validators=[DataRequired()], widget=TextArea())
    slug = StringField("Slug", validators=[DataRequired()])
    submit =SubmitField("Submit")

@app.route('/post/<int:id>')
def post(id):
    post = Posts.query.get_or_404(id)
    return render_template('post.html', post=post)

@app.route('/posts')
def posts():
    # Grab all the posts form 
    posts = Posts.query.order_by(Posts.date_posted)
    return render_template("posts.html", posts=posts)

@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
def edit_post(id):
    post = Posts.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.author = form.author.data
        post.slug = form.slug.data
        post.content = form.content.data
        # Update Database
        db.session.add(post)
        db.session.commit()
        flash("Post Has Been Updated!")
        return redirect(url_for('post', id=post.id))
    form.title.data = post.title
    form.author.data = post.author
    form.slug.data = post.slug
    form.content.data = post.content
    return render_template('edit_post.html', form=form)

# Add Post Page
@app.route('/add-post', methods=['GET', 'POST'])
def add_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Posts(title=form.title.data, author=form.author.data, content=form.content.data, slug=form.slug.data)
        #Clear The Form
        form.title.data = ''
        form.content.data = ''
        form.author.data = ''
        form.slug.data = ''

        # Add post data to the database
        db.session.add(post)
        db.session.commit()
        flash("Blog Post Submitted successfully!")
    return render_template("add_post.html", form=form)




# Json Thing
@app.route('/date')
def get_current_date():
    favourite_pizza={
        "Wilson":"Mushroom",
        "Conner":"Pepperoni",
        "Duchard":"Cheese",
        "Tim": "Pinapple"
    }
    return favourite_pizza

# Creating Model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(300), nullable=False, unique=True)
    favourite_color = db.Column(db.String(120))
    date_added = db.Column(db.DateTime, default=datetime.utcnow())
    # Di Jumbo Passwood!
    password_hash = db.Column(db.String(120))

    @property
    def password(self):
        raise AttributeError('password is not readable attribute!(-<>-)!')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Create A String
    def __repr__(self):
        return '<Name %r>' %self.name

# Create a Form class
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    favourite_color = StringField("Favourite Color")
    password_hash = PasswordField('Password', validators=[DataRequired(), EqualTo('password_hash2', message='password must match')])
    password_hash2 = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField("Submit")

# Create a Form class
class NamerForm(FlaskForm):
    name = StringField("What's Your Name", validators=[DataRequired()])
    submit = SubmitField("Submit")

class PasswordForm(FlaskForm):
    email = StringField("What's Your Email", validators=[DataRequired()])
    password_hash = PasswordField("What's Your Password", validators=[DataRequired()])
    submit = SubmitField("Submit")

# Update Database Record
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favourite_color = request.form['favourite_color']
        try:
            db.session.commit()
            flash("User Updated Successfully!")
            return render_template("update.html", 
                        form=form,
                        name_to_update=name_to_update)
        except:
            db.session.commit()
            flash("Error! Looks like there was a problem...try again! ")
            return render_template("update.html", 
                        form=form,
                        name_to_update=name_to_update)
    else:
       return render_template("update.html", 
                        form=form,
                        name_to_update=name_to_update,
                        id=id )

@app.route('/delete/<int:id>')
def delete(id):
    user_to_delete = Users.query.get_or_404(id)
    name = None
    form = UserForm()
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User Deleted Successfully!!")
        our_users = Users.query.order_by(Users.date_added)
        return render_template("add_user.html", form=form, name=name, our_users=our_users)
    except:
        flash("Whoops!Something has gone terribly wrong!Try Again...")
        return render_template("add_user.html", form=form, name=name, our_users=our_users)


# Create a Name Page
@app.route('/name', methods=['GET', 'POST'])
def name():
    name = None
    form = NamerForm()
    # Validate Form
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        flash("Form Submitted Successfully!") 
    return render_template("name.html", 
                name=name,
                form=form)





# Create a Password Test Page
@app.route('/test_pw', methods=['GET', 'POST'])
def test_pw():
    email = None
    password = None
    pw_to_check = None
    passed = None
    form = PasswordForm()
    # Validate Form
    if form.validate_on_submit():
        email = form.email.data
        password = form.password_hash.data
        form.email.data = ''
        form.password_hash.data = ''
        
        # Lookup for email
        pw_to_check = Users.query.filter_by(email=email).first()

        # Check Hashed Passowrd
        passed = check_password_hash(pw_to_check.password_hash, password)

    return render_template("test_pw.html", 
                email=email,
                password=password,
                pw_to_check=pw_to_check,
                passed=passed,
                form=form)
 
@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            # Hash the password!!!!!
            hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
            user = Users(name=form.name.data, email=form.email.data, favourite_color=form.favourite_color.data, password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.email.data = ''
        form.favourite_color.data = ''
        form.password_hash.data = ''
        flash("User Added Successfully")
    our_users = Users.query.order_by(Users.date_added)
    return render_template("add_user.html", form=form, name=name, our_users=our_users)


# Create a route decorator
@app.route('/')
def index():
    first_name = "Duchard"
    stuff = "This is bold text"
    cool_list = ["ice cream", 'ice block', 'milk shake', 'frozen tea', 'lemon-zero']
    return render_template("index.html", 
                first_name=first_name,
                stuff = stuff,
                cool_list=cool_list)

@app.route('/user/<name>')
def user(name):
    return render_template("user.html", user_name=name)

#Create a custom error pages

# Invaid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

# Internal Server Error
@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500


