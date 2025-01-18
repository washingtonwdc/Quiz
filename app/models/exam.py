from datetime import datetime

class Question:
    def __init__(self, id, text, alternatives, correct_answer):
        self.id = id
        self.text = text
        self.alternatives = alternatives
        self.correct_answer = correct_answer
        self.explanation = None
        self.difficulty = None
        self.tags = []
        self.statistics = QuestionStatistics()

class Exam:
    def __init__(self, id, title, description):
        self.id = id
        self.title = title
        self.description = description
        self.questions = []
        self.duration = None
        self.start_time = None
        self.end_time = None
        self.status = 'draft'
        self.statistics = ExamStatistics()

    def add_question(self, question):
        self.questions.append(question)

    def remove_question(self, question_id):
        self.questions = [q for q in self.questions if q.id != question_id]

    def get_duration(self):
        return self.end_time - self.start_time if self.start_time and self.end_time else None

class ExamAttempt:
    def __init__(self, user_id, exam_id):
        self.user_id = user_id
        self.exam_id = exam_id
        self.start_time = datetime.now()
        self.end_time = None
        self.answers = {}
        self.score = None
        self.status = 'in_progress'

    def submit_answer(self, question_id, answer):
        self.answers[question_id] = answer

    def calculate_score(self, exam):
        correct = 0
        for question_id, answer in self.answers.items():
            question = next((q for q in exam.questions if q.id == question_id), None)
            if question and answer == question.correct_answer:
                correct += 1
        self.score = (correct / len(exam.questions)) * 100 if exam.questions else 0
        return self.score
