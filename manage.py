import os
from flask_script import Manager,\
    Command

from flask_migrate import Migrate,\
    MigrateCommand

from app import app, db

from app.horse import retrieve

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)

class Retrieve(Command):
    "run retrieve subroutine"

    def run(self):
        retrieve()


manager.add_command('test', Retrieve)

if __name__ == '__main__':
    manager.run()
