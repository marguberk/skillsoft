from app.models.user import User
from app.models.skills import Skill, UserSkill, SurveyQuestion, UserAnswer
from app.models.achievements import Achievement, UserAchievement, UserLevel

# Импортируем здесь, чтобы избежать циклических импортов
from app import login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))