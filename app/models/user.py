from flask_login import UserMixin
from bson import ObjectId
from app.routes import login_manager, mongo

class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data.get('_id', ''))
        self.email = user_data.get('email', '')
        self.username = user_data.get('username', '')
        self.role = user_data.get('role', 'user')

    def is_admin(self):
        return self.role == 'admin'

@login_manager.user_loader
def load_user(user_id):
    try:
        user_data = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        if user_data:
            return User(user_data)
    except:
        return None
    return None
