from flask import Flask
from configuration import Configuration
from flask_migrate import Migrate, init, migrate, upgrade
from models import database
from sqlalchemy_utils import database_exists, create_database

app = Flask(__name__)
app.config.from_object(Configuration)

migrateObject = Migrate(app, database)

done = False

while not done:
    try:
        if not database_exists(app.config["SQLALCHEMY_DATABASE_URI"]):
            create_database(app.config["SQLALCHEMY_DATABASE_URI"])
        database.init_app(app)

        with app.app_context() as context:
            init()
            migrate(message="Start migration")
            upgrade()

            database.session.commit()
            done = True
    except Exception as error:
        print(error)
