from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from .extensions import db
from flask_login import current_user, LoginManager
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
        from . import models  # 确保模型注册到db

    # 注册蓝图（提前注册，以便路由可用）
    from app.routes.auth_routes import auth_bp
    from app.routes.agent_routes import agent_bp
    from app.routes.api_routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(agent_bp, url_prefix='/agents')
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # 更完善的CORS配置
    CORS(app,
         resources={
             r"/*": {  # 应用到所有路由
                 "origins": ["http://localhost:5173"],
                 "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                 "allow_headers": ["Content-Type", "Authorization"],
                 "supports_credentials": True,
                 "expose_headers": ["Content-Disposition"]
             }
         })

    # 移除旧的初始化调用
    # TongyiService.initialize(app.config['TONGYI_API_KEY'])

    # 添加请求前初始化钩子（方案一：基于用户ID）
    # 请求前初始化钩子
    login_manager = LoginManager(app)
    @login_manager.user_loader
    def load_user(user_id):
        from .models import User  # 替换成你的 User 模型
        return User.query.get(int(user_id))

    @app.before_request
    def initialize_tongyi_service():
        if current_user.is_authenticated:
            try:
                TongyiService.initialize_with_user_id(current_user.id)
            except Exception as e:
                app.logger.error(f"通义服务初始化失败: {str(e)}")

    return app