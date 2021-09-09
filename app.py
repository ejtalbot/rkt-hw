"""Main module to start flask app"""
from os import path

from connexion import App

basedir = path.abspath(path.dirname(__file__))

# Create the connexion application instance to add swagger validation
connex_app = App(__name__, specification_dir=basedir)
connex_app.add_api("swagger.yml")


if __name__ == "__main__":
    connex_app.run()
