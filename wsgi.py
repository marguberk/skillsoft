import sys
import os

# Добавляем путь к приложению в системные пути
path = '/home/YOUR_PYTHONANYWHERE_USERNAME/skillsoft'
if path not in sys.path:
    sys.path.append(path)

# Импортируем и создаем приложение Flask
from app import create_app
application = create_app()

if __name__ == '__main__':
    application.run()