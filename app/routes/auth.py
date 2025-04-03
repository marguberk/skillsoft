from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from urllib.parse import urlparse
from datetime import datetime
from app import db
from app.forms import LoginForm, RegistrationForm
from app.models.user import User
from app.models.achievements import UserLevel  # Добавляем импорт UserLevel

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Неправильный email или пароль', 'error')
            return redirect(url_for('auth.login'))

        login_user(user, remember=form.remember_me.data)

        # Обновляем статистику входов
        now = datetime.utcnow()
        if user.last_login:
            # Если последний вход был менее 24 часов назад, увеличиваем streak
            if (now - user.last_login).days <= 1:
                user.login_streak += 1
            else:
                user.login_streak = 1
        else:
            user.login_streak = 1

        user.last_login = now
        db.session.commit()

        # Проверяем достижения
        user.check_achievements()

        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('dashboard.index')
        return redirect(next_page)

    return render_template('auth/login.html', form=form)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)

        # Создаем начальный уровень для пользователя
        user_level = UserLevel(current_level=1, current_xp=0)
        user.level = user_level

        db.session.add(user)
        db.session.commit()

        flash('Поздравляем, вы успешно зарегистрировались!', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))