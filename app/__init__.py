from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from .extensions import db
from app.services.tongyi_service import TongyiService

from config import Config

migrate = Migrate()
jwt = JWTManager()




def create_app(config_class):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 初始化扩展
    db.init_app(app)
    jwt.init_app(app)

    with app.app_context():
        from . import models  # 这会确保模型注册到db

    # 初始化通义服务（移到后面）
    from .services.tongyi_service import TongyiService
    TongyiService.initialize(app.config['TONGYI_API_KEY'])

    from app.routes.auth_routes import auth_bp
    from app.routes.agent_routes import agent_bp
    app.register_blueprint(agent_bp, url_prefix='/agents')
    # 根据你的实际路径调整
    app.register_blueprint(auth_bp, url_prefix='/auth')

    return app

