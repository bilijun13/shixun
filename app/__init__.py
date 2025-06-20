from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from config import Config

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # 注册蓝图
    from app.routes.auth_routes import auth_bp
    from app.routes.agent_routes import agent_bp
    from app.routes.api_routes import api_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(agent_bp, url_prefix='/agents')
    app.register_blueprint(api_bp, url_prefix='/api')

    return app

