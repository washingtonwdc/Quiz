from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.user import User
from app.routes import mongo
from bson import ObjectId

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = mongo.db.users.find_one({"email": email})
        
        if user and check_password_hash(user['password'], password):
            user_obj = User(user)
            login_user(user_obj)
            return redirect(url_for('main.dashboard'))
        
        flash('Email ou senha incorretos.', 'danger')
    return render_template('auth/login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        
        if mongo.db.users.find_one({"email": email}):
            flash('Email já cadastrado.', 'danger')
            return redirect(url_for('auth.register'))
        
        new_user = {
            "email": email,
            "username": username,
            "password": generate_password_hash(password),
            "role": "user"
        }
        
        mongo.db.users.insert_one(new_user)
        flash('Cadastro realizado com sucesso!', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html')

@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = mongo.db.users.find_one({"email": email})
        
        if user:
            # Aqui você implementaria o envio do email
            # Por enquanto, apenas simulamos
            flash('Se o email existir, você receberá as instruções de recuperação.', 'info')
            return redirect(url_for('auth.login'))
            
    return render_template('auth/forgot_password.html')

@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    # Implementação futura da redefinição de senha
    return render_template('auth/reset_password.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
