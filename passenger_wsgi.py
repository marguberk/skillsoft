import sys, os

# Добавляем путь к виртуальному окружению
INTERP = os.path.expanduser("/var/www/vhosts/[ваш-домен]/[путь-к-проекту]/venv/bin/python")
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

# Добавляем путь к приложению
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
application = create_app()