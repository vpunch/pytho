from rstapp import create_app
import _celery.tasks  # чтобы Celery смог брать оттуда код задач

celery = create_app().extensions['celery']
