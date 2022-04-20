from email.policy import default
from ssl import OP_SINGLE_DH_USE
from tabnanny import check
from flask import Flask, render_template, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate 
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

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


