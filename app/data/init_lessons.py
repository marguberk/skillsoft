from app import db
from app.models.learning import Lesson, LessonQuiz
from app.models.skills import Skill
from app.data.lessons.communication_basics import LESSON_CONTENT, QUIZ_QUESTIONS

def init_lessons():
    # Получаем навык "Коммуникация"
    communication_skill = Skill.query.filter_by(name='Коммуникация').first()
    if not communication_skill:
        communication_skill = Skill(name='Коммуникация', description='Навыки эффективного общения')
        db.session.add(communication_skill)
        db.session.commit()

    # Создаем первый урок
    lesson = Lesson.query.filter_by(slug='basics-of-effective-communication').first()
    if not lesson:
        lesson = Lesson(
            skill_id=communication_skill.id,
            title='Основы эффективной коммуникации',
            slug='basics-of-effective-communication',
            description='Изучите основные принципы эффективной коммуникации, включая вербальные и невербальные аспекты общения.',
            content=LESSON_CONTENT,
            duration=30,  # в минутах
            difficulty='beginner',
            order=1
        )
        db.session.add(lesson)
        db.session.commit()

        # Добавляем вопросы для теста
        for i, q in enumerate(QUIZ_QUESTIONS, 1):
            quiz = LessonQuiz(
                lesson_id=lesson.id,
                question_type=q.get('question_type', 'single_choice'),  # Добавляем тип вопроса
                question=q['question'],
                options=q['options'],
                correct_answer=q['correct_answer'],
                explanation=q['explanation'],
                order=i
            )
            db.session.add(quiz)
        
        db.session.commit()

if __name__ == '__main__':
    init_lessons() 