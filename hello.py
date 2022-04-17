from ssl import OP_SINGLE_DH_USE
from flask import Flask, render_template

# Create a flask instance
app = Flask(__name__)

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
