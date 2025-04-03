from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
import os
import sys
import datetime

# Добавляем корневую директорию проекта в путь Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

# Инициализация расширений
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()

# Настройка Flask-Login
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Пожалуйста, войдите, чтобы получить доступ к этой странице.'
login_manager.login_message_category = 'info'


def slice_list(lst, start, end):
    """Кастомный фильтр для срезов в шаблонах"""
    return lst[start:end]


@login_manager.user_loader
def load_user(user_id):
    from app.models.user import User
    return User.query.get(int(user_id))


def create_app(test_config=None):
    # Создание экземпляра приложения
    app = Flask(__name__, instance_relative_config=True)

    # Загрузка конфигурации
    app.config.from_object(Config)

    # Инициализация расширений
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Регистрация кастомных фильтров для шаблонов
    app.jinja_env.filters['slice'] = slice_list

    # Регистрация blueprints
    from app.routes.main import bp as main_bp
    from app.routes.auth import bp as auth_bp
    from app.routes.dashboard import bp as dashboard_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)

    # Инициализация базы данных
    with app.app_context():
        db.create_all()  # Создаем все таблицы

        # Теперь проверяем наличие данных и создаем начальные данные если нужно
        from app.models.skills import Skill
        if not Skill.query.first():
            # Создаем начальные достижения
            from app.models.achievements import Achievement
            from app.data.achievements import INITIAL_ACHIEVEMENTS
            for achievement_data in INITIAL_ACHIEVEMENTS:
                achievement = Achievement(**achievement_data)
                db.session.add(achievement)

            # Создаем начальные навыки
            default_skills = [
                Skill(name='Коммуникация', description='Способность эффективно общаться с другими', category='soft'),
                Skill(name='Лидерство', description='Способность вести и мотивировать команду', category='soft'),
                Skill(name='Адаптивность', description='Способность приспосабливаться к изменениям', category='soft'),
                Skill(name='Критическое мышление', description='Способность анализировать и решать проблемы',
                      category='soft'),
                Skill(name='Тайм-менеджмент', description='Способность управлять временем и приоритетами',
                      category='soft')
            ]

            for skill in default_skills:
                db.session.add(skill)

            # Создаем шаблоны ежедневных заданий
            from app.models.daily_tasks import DailyTask
            from app.data.daily_tasks import DAILY_TASK_TEMPLATES

            for skill_name, tasks in DAILY_TASK_TEMPLATES.items():
                skill = Skill.query.filter_by(name=skill_name).first()
                if skill:
                    for task_data in tasks:
                        task = DailyTask(
                            title=task_data['title'],
                            description=task_data['description'],
                            skill_id=skill.id,
                            difficulty=task_data['difficulty'],
                            xp_reward=task_data['xp_reward']
                        )
                        db.session.add(task)

            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(f"Ошибка при инициализации базы данных: {e}")

    # Обработчики ошибок
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    # Контекстный процессор для добавления глобальных переменных в шаблоны
    @app.context_processor
    def utility_processor():
        return {
            'app_name': 'SkillSoft',
            'current_year': datetime.datetime.now().year
        }

    # Инициализация админки
    from app.admin import init_admin
    admin = init_admin(app)

    # Регистрация команд
    from . import cli
    cli.init_app(app)

    return app