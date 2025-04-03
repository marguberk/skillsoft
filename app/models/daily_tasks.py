from app import db
from datetime import datetime, timedelta


class DailyTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    skill_id = db.Column(db.Integer, db.ForeignKey('skill.id'))
    xp_reward = db.Column(db.Integer, default=50)
    difficulty = db.Column(db.String(20))  # easy, medium, hard
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Связи
    skill = db.relationship('Skill', backref='tasks')
    user_tasks = db.relationship('UserDailyTask', backref='task', lazy='dynamic')


class UserDailyTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('daily_task.id'), nullable=False)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    is_completed = db.Column(db.Boolean, default=False)

    @property
    def is_expired(self):
        return datetime.utcnow() > self.assigned_at + timedelta(days=1)