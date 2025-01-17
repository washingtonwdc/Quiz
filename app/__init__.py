from flask import Flask
from flask_wtf import CSRFProtect

# __init__.py


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'

csrf = CSRFProtect(app)
