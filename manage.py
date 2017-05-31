import os

from flask_script import Manager,\
    Command

from flask_migrate import Migrate,\
    MigrateCommand

from app.models import Article

from app import app,\
    db,\
    __init__

from app.jobs.horse import retrieve

manager = Manager(app)
migrate = Migrate(app, db)

class Retrieve(Command):
    "Run retrieve subroutine"

    def run(self):
        retrieve()

manager.add_command('db', MigrateCommand)
manager.add_command('retrieve', Retrieve)

def run_server():
    try:
        __init__()
    except Exception as e:
        print(e)
    manager.run()

if __name__ == '__main__':
    run_server()
