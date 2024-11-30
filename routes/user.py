from flask import Blueprint, request, render_template, redirect, url_for, Request, Response, session, g

from flask_mysqldb import MySQL

from controller.user_manager import UserManager
from app import dao

user = Blueprint('user', __name__, template_folder='templates')

user_controller = UserManager(dao)

@user.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'GET':
        return render_template('signin.html')
    print(request.form)
    email = request.form['email']
    password = request.form['password']
    error, user = user_controller.validate_user(email, password)
    if error is not None:
        return render_template('signin.html', error=error)
    session['user'] = user[2]
    session['logged_in'] = True
    session['id'] = user[4]
    return redirect('/')


@user.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    email = request.form['email']
    name = request.form['name']
    password = request.form['password']
    password_confirm = request.form['password_confirm']
    if password != password_confirm:
        return render_template('signup.html', error="Passwords do not match")
    error = user_controller.insert_user(email, password, name)
    if error is not None:
        return render_template('signup.html', error=error)
    return render_template('signin.html', success="Account created successfully")

@user.route('/signout', methods=['GET'])
def signout():
    if 'id' in session:
        del session['id']
        del session['user']
        del session['logged_in']
    return redirect('/signin')
    