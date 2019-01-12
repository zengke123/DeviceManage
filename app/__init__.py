from flask import Flask
from flask_admin import Admin
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import config

# 创建SQLAlchemy实例
db = SQLAlchemy()
# 创建后台管理实例
admin = Admin(name='后台管理', template_mode='bootstrap3')
# 创建用户管理
login_manager = LoginManager()
login_manager.session_protection = 'strong'
# 登录视图对应蓝图auth的login
login_manager.login_view = 'auth.login'


def create_app():
    app = Flask(__name__)
    app.config.from_object(config)
    # 初始化数据库
    db.init_app(app)
    # 初始化后台管理admin
    admin.init_app(app)
    # 初始化用户管理
    login_manager.init_app(app)
    # 蓝本注册
    from .main import main as main_blueprint
    from .operate import operate as operate_blueprint
    from .auth import auth as auth_blueprint
    app.register_blueprint(main_blueprint, url_prefix='/info')
    app.register_blueprint(operate_blueprint, url_prefix='/operate')
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    return app