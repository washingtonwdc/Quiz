from app import app, db
from app.models import Quiz, Question, Option

with app.app_context():
	db.create_all()
	print("Database initialized!")
