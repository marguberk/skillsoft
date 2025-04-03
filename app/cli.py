import click
from flask.cli import with_appcontext
from app.data.init_lessons import init_lessons

def init_app(app):
    app.cli.add_command(init_lessons_command)

@click.command('init-lessons')
@with_appcontext
def init_lessons_command():
    """Инициализация уроков в базе данных."""
    init_lessons()
    click.echo('Уроки успешно инициализированы.') 