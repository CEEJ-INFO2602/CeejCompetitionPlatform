from flask import Blueprint, render_template, jsonify, request, send_from_directory, flash, redirect, url_for
from flask_jwt_extended import jwt_required, current_user as jwt_current_user
from flask_login import login_required, login_user, current_user, logout_user
from App.models import User

from.index import index_views

from App.controllers import (
    create_user,
    jwt_authenticate,
    login, 
    get_active_user,
    set_active_true,
    set_active_false
)

auth_views = Blueprint('auth_views', __name__, template_folder='../templates')

'''
Page/Action Routes
'''

@auth_views.route('/users', methods=['GET'])
def get_user_page():
    users = get_all_users()
    return render_template('users.html', users=users)


@auth_views.route('/identify', methods=['GET'])
@login_required
def identify_page():
    return jsonify({'message': f"username: {current_user.username}, id : {current_user.id}"})


@auth_views.route('/render_login', methods=['GET'])
def render_login():
    return render_template('loginPage.html')

@auth_views.route('/login_action', methods=['GET', 'POST'])
def login_action():
    data = request.form
    user = login(data['username'], data['password'])
    if user:
        login_user(user)
        set_active_true(user)
        return render_template('competitionsPage.html'), 200
    
    flash('bad username or password given')
    return render_template('loginPage.html'), 401

@auth_views.route('/logout_action')
def logout_action():
    logout_user()
    return render_template('index.html')

@auth_views.route('/render_signUp', methods=['GET'])
def render_signUp():
    return render_template('signUpPage.html')

@auth_views.route('/signUp_action', methods=['GET', 'POST'])
def signUp_action():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirmPassword = request.form.get('confirmPassword')

        if (password != confirmPassword):
            flash('Passwords do not match')
            return render_template('signUpPage.html'), 401


        # Check if username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username Already Taken !!!')
            return render_template('signUpPage.html'), 401

        # Create a new user & Save the new user to the database
        create_user(username, password, access ="user")

        # Log in the user
        user=login(username, password)

        login_user(user)
        set_active_true(user)
        return render_template('competitionsPage.html'), 200

    flask('ERROR SIGNING UP!')
    return render_template('signUpPage.html'), 401

@auth_views.route('/active_user', methods=['GET', 'POST'])
def active_user():
    username = get_active_user()
    return username


@auth_views.route('/competitionsPage', methods=['GET', 'POST'])
def competitionsPage():
    username = get_active_user()
    return render_template('competitionsPage.html', username=username)


'''
API Routes
'''

@auth_views.route('/api/users', methods=['GET'])
def get_users_action():
    users = get_all_users_json()
    return jsonify(users)

@auth_views.route('/api/users', methods=['POST'])
def create_user_endpoint():
    data = request.json
    create_user(data['username'], data['password'])
    return jsonify({'message': f"user {data['username']} created"})

@auth_views.route('/api/login', methods=['POST'])
def user_login_api():
  data = request.json
  token = jwt_authenticate(data['username'], data['password'])
  if not token:
    return jsonify(message='bad username or password given'), 401
  return jsonify(access_token=token)

@auth_views.route('/api/identify', methods=['GET'])
@jwt_required()
def identify_user_action():
    return jsonify({'message': f"username: {jwt_current_user.username}, id : {jwt_current_user.id}"})