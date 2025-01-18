from functools import wraps
from flask import session, redirect, url_for, flash
import jwt
from datetime import datetime, timedelta
from app.config import SECRET_KEY

class AuthService:
    @staticmethod
    def login_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Por favor, faça login para acessar esta página.', 'warning')
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function

    @staticmethod
    def generate_token(user_id):
        return jwt.encode(
            {
                'user_id': user_id,
                'exp': datetime.utcnow() + timedelta(days=1)
            },
            SECRET_KEY,
            algorithm='HS256'
        )

    @staticmethod
    def verify_token(token):
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            return data['user_id']
        except:
            return None
