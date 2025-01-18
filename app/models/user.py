from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User:
    def __init__(self, id, username, email, created_at=None):
        self.id = id
        self.username = username
        self.email = email
        self.created_at = created_at or datetime.now()
        self._password = None
        self.profile = None
        self.progress = {}
        self.preferences = {}

    def set_password(self, password):
        self._password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self._password, password)

    def get_progress(self, subject=None):
        if subject:
            return self.progress.get(subject, 0)
        return sum(self.progress.values()) / len(self.progress) if self.progress else 0

    def update_progress(self, subject, value):
        self.progress[subject] = value

class UserProfile:
    def __init__(self, user_id):
        self.user_id = user_id
        self.bio = ""
        self.avatar_url = None
        self.social_links = {}
        self.study_goals = []
        self.achievements = []
