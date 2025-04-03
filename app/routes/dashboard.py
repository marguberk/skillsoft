from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from app import db
from app.models.user import User
from app.models.skills import Skill, UserSkill, SurveyQuestion, UserAnswer
from app.models.achievements import Achievement, UserAchievement
from app.models.daily_tasks import DailyTask, UserDailyTask
from app.forms import SurveyForm
from app.data.survey_questions import SURVEY_QUESTIONS
from app.data.learning_materials import LEARNING_MATERIALS, get_level_category
import random
from app.models.learning import Lesson, LessonProgress, LessonQuiz, QuizAttempt

bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


@bp.route('/')
@login_required
def index():
    current_user.last_seen = datetime.utcnow()
    db.session.commit()
    return render_template('dashboard/index.html')


@bp.route('/start-survey')
@login_required
def start_survey():
    if current_user.completed_survey:
        flash('Вы уже прошли оценку навыков', 'info')
        return redirect(url_for('dashboard.index'))

    # Создаем вопросы в базе данных, если их еще нет
    if not SurveyQuestion.query.first():
        for skill_name, questions in SURVEY_QUESTIONS.items():
            skill = Skill.query.filter_by(name=skill_name).first()
            if skill:
                for q in questions:
                    question = SurveyQuestion(
                        question=q['question'],
                        skill_id=skill.id,
                        weight=q['weight']
                    )
                    db.session.add(question)
        db.session.commit()

    return redirect(url_for('dashboard.survey'))


@bp.route('/survey', methods=['GET', 'POST'])
@login_required
def survey():
    if current_user.completed_survey:
        return redirect(url_for('dashboard.index'))

    form = SurveyForm()

    # Получаем все вопросы и группируем их по навыкам
    questions = SurveyQuestion.query.join(Skill).all()
    grouped_questions = {}
    for question in questions:
        if question.skill.name not in grouped_questions:
            grouped_questions[question.skill.name] = []
        grouped_questions[question.skill.name].append(question)

    if form.validate_on_submit():
        # Проверяем, что есть ответы на все вопросы
        all_answered = True
        missing_answers = []

        for question in questions:
            answer = request.form.get(f'question_{question.id}')
            if not answer:
                all_answered = False
                missing_answers.append(question.question)

        if not all_answered:
            flash('Пожалуйста, ответьте на все вопросы:', 'error')
            for missing in missing_answers:
                flash(f'- {missing}', 'error')
            return render_template(
                'dashboard/survey.html',
                form=form,
                grouped_questions=grouped_questions,
                total_questions=len(questions)
            )

        # Обработка ответов
        skill_scores = {}
        try:
            for question in questions:
                answer_value = int(request.form.get(f'question_{question.id}'))
                if not 1 <= answer_value <= 5:
                    raise ValueError(f"Некорректное значение ответа: {answer_value}")

                # Сохраняем ответ
                user_answer = UserAnswer(
                    user_id=current_user.id,
                    question_id=question.id,
                    answer_value=answer_value
                )
                db.session.add(user_answer)

                # Рассчитываем взвешенный балл
                weighted_score = answer_value * question.weight
                if question.skill_id not in skill_scores:
                    skill_scores[question.skill_id] = {'total': 0, 'count': 0}
                skill_scores[question.skill_id]['total'] += weighted_score
                skill_scores[question.skill_id]['count'] += 1

            # Сохраняем результаты по каждому навыку
            for skill_id, scores in skill_scores.items():
                average_score = (scores['total'] / scores['count'])
                # Переводим в проценты (1-5 -> 0-100)
                skill_level = int((average_score - 1) * 25)

                user_skill = UserSkill(
                    user_id=current_user.id,
                    skill_id=skill_id,
                    level=skill_level
                )
                db.session.add(user_skill)

            # Отмечаем, что пользователь прошел опрос
            current_user.completed_survey = True
            db.session.commit()

            # Начисляем XP за прохождение опроса
            if hasattr(current_user, 'add_xp'):
                current_user.add_xp(100)  # 100 XP за прохождение опроса

            flash('Оценка навыков успешно завершена!', 'success')
            return redirect(url_for('dashboard.index'))

        except (ValueError, TypeError) as e:
            db.session.rollback()
            flash(f'Произошла ошибка при обработке ответов: {str(e)}', 'error')
            return render_template(
                'dashboard/survey.html',
                form=form,
                grouped_questions=grouped_questions,
                total_questions=len(questions)
            )

    return render_template(
        'dashboard/survey.html',
        form=form,
        grouped_questions=grouped_questions,
        total_questions=len(questions)
    )


@bp.route('/learning')
@login_required
def learning():
    # Получаем все навыки с их уроками
    skills = Skill.query.all()
    
    return render_template('dashboard/learning.html', skills=skills)


@bp.route('/achievements')
@login_required
def achievements():
    # Проверяем достижения пользователя
    if hasattr(current_user, 'check_achievements'):
        current_user.check_achievements()

    # Получаем все достижения и статус их получения пользователем
    achievements = Achievement.query.all()
    user_achievements = current_user.achievements.all() if hasattr(current_user, 'achievements') else []
    user_achievement_dict = {ua.achievement_id: ua for ua in user_achievements}

    return render_template(
        'dashboard/achievements.html',
        achievements=achievements,
        user_achievements=user_achievement_dict,
        user_level=current_user.level
    )


@bp.route('/daily-tasks')
@login_required
def daily_tasks():
    # Очищаем просроченные задания
    expired_tasks = UserDailyTask.query.filter(
        UserDailyTask.user_id == current_user.id,
        UserDailyTask.is_completed == False,
        UserDailyTask.assigned_at < datetime.utcnow() - timedelta(days=1)
    ).all()

    for task in expired_tasks:
        db.session.delete(task)

    # Получаем текущие задания пользователя
    user_tasks = UserDailyTask.query.filter(
        UserDailyTask.user_id == current_user.id,
        UserDailyTask.is_completed == False,
        UserDailyTask.assigned_at >= datetime.utcnow() - timedelta(days=1)
    ).all()

    # Если у пользователя нет активных заданий, генерируем новые
    if not user_tasks:
        available_tasks = DailyTask.query.all()
        if available_tasks:
            # Выбираем 3 случайных задания
            selected_tasks = random.sample(available_tasks, min(3, len(available_tasks)))

            for task in selected_tasks:
                user_task = UserDailyTask(user_id=current_user.id, task_id=task.id)
                db.session.add(user_task)

            db.session.commit()
            user_tasks = UserDailyTask.query.filter(
                UserDailyTask.user_id == current_user.id,
                UserDailyTask.is_completed == False
            ).all()

    return render_template('dashboard/daily_tasks.html',
                           user_tasks=user_tasks,
                           now=datetime.utcnow(),
                           timedelta=timedelta)


@bp.route('/complete-task/<int:task_id>', methods=['POST'])
@login_required
def complete_task(task_id):
    user_task = UserDailyTask.query.filter_by(
        user_id=current_user.id,
        task_id=task_id,
        is_completed=False
    ).first_or_404()

    if user_task.is_expired:
        flash('Время выполнения задания истекло', 'error')
        return redirect(url_for('dashboard.daily_tasks'))

    user_task.is_completed = True
    user_task.completed_at = datetime.utcnow()

    # Начисляем награду
    task = DailyTask.query.get(task_id)
    if task:
        if hasattr(current_user, 'add_xp'):
            current_user.add_xp(task.xp_reward)
        flash(f'Поздравляем! Вы получили {task.xp_reward} XP за выполнение задания!', 'success')

    db.session.commit()
    return redirect(url_for('dashboard.daily_tasks'))


@bp.route('/lesson/<string:slug>')
@login_required
def lesson(slug):
    try:
        lesson = Lesson.query.filter_by(slug=slug).first_or_404()
        
        # Получаем или создаем прогресс пользователя
        progress = LessonProgress.query.filter_by(
            user_id=current_user.id,
            lesson_id=lesson.id
        ).first()
        
        if not progress:
            progress = LessonProgress(
                user_id=current_user.id,
                lesson_id=lesson.id,
                status='in_progress'
            )
            db.session.add(progress)
            db.session.commit()
        
        # Получаем вопросы для урока
        quiz_questions = LessonQuiz.query.filter_by(lesson_id=lesson.id).order_by(LessonQuiz.order).all()
        
        return render_template('dashboard/lesson.html',
                             lesson=lesson,
                             progress=progress,
                             quiz_questions=quiz_questions)
    except Exception as e:
        db.session.rollback()
        print(f"Error in lesson route: {str(e)}")  # Для отладки
        return render_template('errors/500.html'), 500


@bp.route('/lesson/<string:slug>/progress', methods=['POST'])
@login_required
def update_lesson_progress(slug):
    try:
        lesson = Lesson.query.filter_by(slug=slug).first_or_404()
        progress = LessonProgress.query.filter_by(
            user_id=current_user.id,
            lesson_id=lesson.id
        ).first_or_404()
        
        data = request.get_json()
        new_progress = data.get('progress', 0)
        
        if new_progress == 100:
            progress.status = 'completed'
            progress.completed_at = datetime.utcnow()
        else:
            progress.status = 'in_progress'
        
        progress.progress = new_progress
        progress.last_activity = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'status': 'success'})
    except Exception as e:
        db.session.rollback()
        print(f"Error in update_lesson_progress: {str(e)}")  # Для отладки
        return jsonify({'status': 'error', 'message': str(e)}), 500


@bp.route('/lesson/<string:slug>/quiz', methods=['POST'])
@login_required
def submit_quiz(slug):
    try:
        lesson = Lesson.query.filter_by(slug=slug).first_or_404()
        data = request.get_json()
        
        question_id = data.get('question_id')
        answer = data.get('answer')
        
        question = LessonQuiz.query.get_or_404(question_id)
        is_correct = question.check_answer(answer)
        
        attempt = QuizAttempt(
            user_id=current_user.id,
            question_id=question_id,
            answer=answer,
            is_correct=is_correct
        )
        db.session.add(attempt)
        db.session.commit()
        
        return jsonify({
            'is_correct': is_correct,
            'explanation': question.explanation if not is_correct else None
        })
    except Exception as e:
        db.session.rollback()
        print(f"Error in submit_quiz: {str(e)}")  # Для отладки
        return jsonify({'status': 'error', 'message': str(e)}), 500