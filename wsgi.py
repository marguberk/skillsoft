import os
import sys

# Путь к директории с приложением
path = '/home/marguberk/skillsoft'
if path not in sys.path:
    sys.path.append(path)

# Активируем виртуальное окружение
VIRTUALENV = '/home/marguberk/.virtualenvs/skillsoft-env'
if os.path.exists(VIRTUALENV):
    activate_this = os.path.join(VIRTUALENV, 'bin/activate_this.py')
    if os.path.exists(activate_this):
        with open(activate_this) as file_:
            exec(file_.read(), dict(__file__=activate_this))

# Устанавливаем переменные окружения
os.environ['FLASK_APP'] = 'app'
os.environ['FLASK_ENV'] = 'production'
os.environ.setdefault('FLASK_SETTINGS_MODULE', 'config.ProductionConfig')

# Импортируем и создаем приложение Flask
from app import create_app
application = create_app()

if __name__ == '__main__':
    application.run()