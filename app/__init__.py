from flask import Flask
from flask_admin import Admin
from flask_sqlalchemy import SQLAlchemy
import config

db = SQLAlchemy()
admin = Admin(name='后台管理', template_mode='bootstrap3')


def create_app():
    app = Flask(__name__)
    app.config.from_object(config)
    app.config.from_object(config)
    db.init_app(app)
    admin.init_app(app)
    from .main import main as main_blueprint
    from .operate import operate as operate_blueprint
    app.register_blueprint(main_blueprint, url_prefix='/info')
    app.register_blueprint(operate_blueprint, url_prefix='/operate')
    return app