INITIAL_ACHIEVEMENTS = [
    {
        'name': 'Первые шаги',
        'description': 'Пройдите первую оценку навыков',
        'icon': 'award',
        'points': 100,
        'condition_type': 'completed_survey',
        'condition_value': 1
    },
    {
        'name': 'Мастер навыка',
        'description': 'Достигните уровня 70 в любом навыке',
        'icon': 'star',
        'points': 500,
        'condition_type': 'skill_level',
        'condition_value': 70
    },
    {
        'name': 'Постоянный ученик',
        'description': 'Заходите в систему 7 дней подряд',
        'icon': 'calendar',
        'points': 300,
        'condition_type': 'login_streak',
        'condition_value': 7
    }
]