from app import db
from datetime import datetime

class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    skill_id = db.Column(db.Integer, db.ForeignKey('skill.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    description = db.Column(db.Text)
    content = db.Column(db.Text)
    duration = db.Column(db.Integer)  # в минутах
    difficulty = db.Column(db.String(50))
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Отношения
    skill = db.relationship('Skill', backref='lessons')
    progress = db.relationship('LessonProgress', backref='lesson', lazy='dynamic')

    def __repr__(self):
        return f'<Lesson {self.title}>'


class LessonProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=False)
    status = db.Column(db.String(20), default='not_started')  # not_started, in_progress, completed
    progress = db.Column(db.Integer, default=0)  # процент выполнения
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Уникальный индекс для пары пользователь-урок
    __table_args__ = (db.UniqueConstraint('user_id', 'lesson_id', name='_user_lesson_uc'),)

    def __repr__(self):
        return f'<LessonProgress {self.user_id}:{self.lesson_id}>'


class LessonQuiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=False)
    question_type = db.Column(db.String(50), default='single_choice')
    question = db.Column(db.Text, nullable=False)
    options = db.Column(db.JSON)
    correct_answer = db.Column(db.JSON)
    explanation = db.Column(db.Text)
    order = db.Column(db.Integer, default=0)

    lesson = db.relationship('Lesson', backref='quiz_questions')

    def __repr__(self):
        return f'<LessonQuiz {self.id}>'

    def check_answer(self, answer):
        """Проверяет ответ в зависимости от типа вопроса"""
        try:
            if not self.correct_answer:
                return False
                
            if self.question_type == 'single_choice':
                return str(answer).lower() == str(self.correct_answer).lower()
                
            elif self.question_type == 'multiple_choice':
                if not isinstance(answer, (list, tuple)) or not isinstance(self.correct_answer, (list, tuple)):
                    return False
                user_answers = set(str(a).lower() for a in answer)
                correct_answers = set(str(a).lower() for a in self.correct_answer)
                return user_answers == correct_answers
                
            elif self.question_type == 'matching':
                if not isinstance(answer, list) or not isinstance(self.correct_answer, list):
                    return False
                if len(answer) != len(self.correct_answer):
                    return False
                return all(
                    str(user_match.get('left', '')).lower() == str(correct_match.get('left', '')).lower() and
                    str(user_match.get('right', '')).lower() == str(correct_match.get('right', '')).lower()
                    for user_match, correct_match in zip(answer, self.correct_answer)
                )
                
            elif self.question_type == 'flashcard':
                if not isinstance(self.correct_answer, dict):
                    return False
                return str(answer).lower() == str(self.correct_answer.get('back', '')).lower()
                
            elif self.question_type == 'ordering':
                if not isinstance(answer, list) or not isinstance(self.correct_answer, list):
                    return False
                if len(answer) != len(self.correct_answer):
                    return False
                return [str(item).lower() for item in answer] == [str(item).lower() for item in self.correct_answer]
                
            return False
            
        except (AttributeError, TypeError, ValueError) as e:
            print(f"Error checking answer for question {self.id}: {str(e)}")
            return False


class QuizAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('lesson_quiz.id'), nullable=False)
    answer = db.Column(db.JSON)  # Сохраняем ответ в формате JSON для поддержки разных типов вопросов
    is_correct = db.Column(db.Boolean)
    attempted_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<QuizAttempt {self.user_id}:{self.question_id}>' 