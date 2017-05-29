import os

from flask_script import Manager,\
    Command

from flask_migrate import Migrate,\
    MigrateCommand

from app.models import Article

from app import app,\
    db,\
    __init__

from app.jobs.horse import retrieve,\
    upload_all

manager = Manager(app)
migrate = Migrate(app, db)

class Retrieve(Command):
    "Run retrieve subroutine"

    def run(self):
        retrieve(first_call=True)

class Upload(Command):
    """
    Run upload subroutine, and  provides S3 management tools
    """

    def run(self):
        upload_all()

manager.add_command('db', MigrateCommand)
manager.add_command('retrieve', Retrieve)
manager.add_command('upload', Upload)

if __name__ == '__main__':
    manager.run()
