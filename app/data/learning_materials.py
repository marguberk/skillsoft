LEARNING_MATERIALS = {
    'Коммуникация': {
        'beginner': [
            {
                'type': 'article',
                'title': 'Основы эффективной коммуникации',
                'description': 'Базовые принципы и техники общения',
                'duration': '10 минут',
                'difficulty': 'легкий'
            },
            {
                'type': 'video',
                'title': 'Как начать говорить уверенно',
                'description': 'Практические упражнения для развития навыков общения',
                'duration': '15 минут',
                'difficulty': 'легкий'
            }
        ],
        'intermediate': [
            {
                'type': 'exercise',
                'title': 'Активное слушание',
                'description': 'Практика техник активного слушания',
                'duration': '30 минут',
                'difficulty': 'средний'
            }
        ],
        'advanced': [
            {
                'type': 'practice',
                'title': 'Публичные выступления',
                'description': 'Подготовка и проведение презентаций',
                'duration': '60 минут',
                'difficulty': 'сложный'
            }
        ]
    },
    # Добавьте аналогичные материалы для других навыков
}

def get_level_category(skill_level):
    if skill_level < 40:
        return 'beginner'
    elif skill_level < 70:
        return 'intermediate'
    else:
        return 'advanced'