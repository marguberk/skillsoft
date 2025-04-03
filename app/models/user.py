from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    completed_survey = db.Column(db.Boolean, default=False)
    login_streak = db.Column(db.Integer, default=0)
    last_login = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)

    # Отношения
    skills = db.relationship('UserSkill', back_populates='user', lazy='dynamic')
    achievements = db.relationship('UserAchievement', backref='user', lazy='dynamic')
    level = db.relationship('UserLevel', uselist=False, backref='user')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def add_xp(self, amount):
        """Добавляет опыт пользователю и обновляет уровень"""
        from app.models.achievements import UserLevel
        if not self.level:
            self.level = UserLevel(user_id=self.id)
            db.session.add(self.level)

        self.level.current_xp += amount
        while self.level.current_xp >= self.level.xp_to_next_level:
            self.level.current_xp -= self.level.xp_to_next_level
            self.level.current_level += 1
        db.session.commit()

    def check_achievements(self):
        """Проверяет и выдает достижения пользователю"""
        from app.models.achievements import Achievement, UserAchievement

        all_achievements = Achievement.query.all()
        for achievement in all_achievements:
            if not self.has_achievement(achievement.id):
                if self.meets_achievement_condition(achievement):
                    self.award_achievement(achievement)

    def has_achievement(self, achievement_id):
        """Проверяет, есть ли у пользователя достижение"""
        return self.achievements.filter_by(achievement_id=achievement_id).first() is not None

    def meets_achievement_condition(self, achievement):
        """Проверяет, выполнены ли условия для получения достижения"""
        if achievement.condition_type == 'completed_survey':
            return self.completed_survey
        elif achievement.condition_type == 'skill_level':
            return any(skill.level >= achievement.condition_value for skill in self.skills)
        elif achievement.condition_type == 'login_streak':
            return self.login_streak >= achievement.condition_value
        return False

    def award_achievement(self, achievement):
        """Выдает достижение пользователю"""
        from app.models.achievements import UserAchievement

        user_achievement = UserAchievement(user_id=self.id, achievement_id=achievement.id)
        db.session.add(user_achievement)
        self.add_xp(achievement.points)  # Начисляем XP за достижение
        db.session.commit()


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))