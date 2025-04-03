from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask import redirect, url_for
from app import db
from app.models.user import User
from app.models.skills import Skill, UserSkill, SurveyQuestion
from app.models.daily_tasks import DailyTask
from app.models.achievements import Achievement


# Базовый класс для всех моделей админки
class SecureModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth.login'))


# Кастомная главная страница админки
class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not current_user.is_authenticated or not current_user.is_admin:
            return redirect(url_for('auth.login'))
        return self.render('admin/index.html')


# Специфические настройки для разных моделей
class UserModelView(SecureModelView):
    column_exclude_list = ['password_hash']
    column_searchable_list = ['username', 'email']
    column_filters = ['is_active', 'completed_survey']
    can_create = True
    can_edit = True
    can_delete = False


class SurveyQuestionModelView(SecureModelView):
    column_searchable_list = ['question']
    column_filters = ['skill']
    form_columns = ['question', 'skill', 'weight']


class SkillModelView(SecureModelView):
    column_searchable_list = ['name']
    column_filters = ['category']
    form_columns = ['name', 'description', 'category']


class DailyTaskModelView(SecureModelView):
    column_searchable_list = ['title']
    column_filters = ['difficulty', 'skill']
    form_columns = ['title', 'description', 'skill', 'difficulty', 'xp_reward']


def init_admin(app):
    admin = Admin(
        app,
        name='SkillSoft Admin',
        template_mode='bootstrap4',
        index_view=MyAdminIndexView()
    )

    # Добавляем модели в админку
    admin.add_view(UserModelView(User, db.session, name='Пользователи'))
    admin.add_view(SkillModelView(Skill, db.session, name='Навыки'))
    admin.add_view(SurveyQuestionModelView(SurveyQuestion, db.session, name='Вопросы теста'))
    admin.add_view(DailyTaskModelView(DailyTask, db.session, name='Ежедневные задания'))
    admin.add_view(SecureModelView(Achievement, db.session, name='Достижения'))

    return admin