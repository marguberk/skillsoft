from app import db
from datetime import datetime


class Achievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(100))
    points = db.Column(db.Integer, default=0)
    condition_type = db.Column(db.String(50))
    condition_value = db.Column(db.Integer)

    user_achievements = db.relationship('UserAchievement', backref='achievement', lazy='dynamic')


class UserAchievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievement.id'), nullable=False)
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)


class UserLevel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    current_level = db.Column(db.Integer, default=1)
    current_xp = db.Column(db.Integer, default=0)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def xp_to_next_level(self):
        return self.current_level * 1000

    @property
    def progress_percentage(self):
        return (self.current_xp / self.xp_to_next_level) * 100