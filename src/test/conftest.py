import pytest
from flask import Flask

from controller.assets_controller import assets_bp
from controller.portfolios_controller import portfolios_bp
from controller.transactions_controller import transactions_bp


@pytest.fixture
def app():
    flask_app = Flask(__name__)
    flask_app.register_blueprint(assets_bp)
    flask_app.register_blueprint(portfolios_bp)
    flask_app.register_blueprint(transactions_bp)
    return flask_app


@pytest.fixture
def app_context(app):
    with app.app_context():
        yield
