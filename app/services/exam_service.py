from app.models.exam import Exam, Question, ExamAttempt

class ExamService:
    def __init__(self):
        self.exams = {}
        self.attempts = {}

    def create_exam(self, title, description, questions):
        exam_id = len(self.exams) + 1
        exam = Exam(exam_id, title, description)
        for q in questions:
            exam.add_question(Question(**q))
        self.exams[exam_id] = exam
        return exam

    def start_attempt(self, user_id, exam_id):
        if exam_id not in self.exams:
            raise ValueError("Exam not found")
        
        attempt = ExamAttempt(user_id, exam_id)
        attempt_id = len(self.attempts) + 1
        self.attempts[attempt_id] = attempt
        return attempt_id

    def submit_answer(self, attempt_id, question_id, answer):
        if attempt_id not in self.attempts:
            raise ValueError("Attempt not found")
        
        attempt = self.attempts[attempt_id]
        attempt.submit_answer(question_id, answer)
        return True

    def finish_attempt(self, attempt_id):
        if attempt_id not in self.attempts:
            raise ValueError("Attempt not found")
        
        attempt = self.attempts[attempt_id]
        exam = self.exams[attempt.exam_id]
        score = attempt.calculate_score(exam)
        attempt.end_time = datetime.now()
        attempt.status = 'completed'
        return score
