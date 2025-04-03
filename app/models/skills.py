from app import db
from datetime import datetime


class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(64))

    # Отношение к пользовательским навыкам
    user_skills = db.relationship('UserSkill', back_populates='skill')


class UserSkill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skill.id'), nullable=False)
    level = db.Column(db.Integer, default=0)  # 0-100
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

    # Определяем отношения
    user = db.relationship('User', back_populates='skills')
    skill = db.relationship('Skill', back_populates='user_skills')


class SurveyQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skill.id'), nullable=False)
    weight = db.Column(db.Float, default=1.0)

    skill = db.relationship('Skill')


class UserAnswer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('survey_question.id'), nullable=False)
    answer_value = db.Column(db.Integer)  # 1-5 например
    created_at = db.Column(db.DateTime, default=datetime.utcnow)