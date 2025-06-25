import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class Config:
    # 安全配置
    SECRET_KEY = os.getenv('SECRET_KEY')


    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'fallback-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_TOKEN_LOCATION = ['headers']  # 双保险
    JWT_COOKIE_SECURE = False  # 开发环境为 False，生产环境必须 True
    JWT_COOKIE_HTTPONLY = True
    JWT_COOKIE_CSRF_PROTECT = False
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_ACCESS_COOKIE_NAME = 'access_token_cookie'  # 明确命名
    JWT_REFRESH_COOKIE_NAME = 'refresh_token_cookie'
    JWT_COOKIE_DOMAIN = 'localhost'
    # 确保 Cookie 路径正确
    JWT_ACCESS_COOKIE_PATH = '/'
    JWT_REFRESH_COOKIE_PATH = '/'

    # JWT增强配置

    JWT_COOKIE_SAMESITE = 'Lax'  # 平衡安全与跨站请求
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'



    # OpenAI
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    # 通义
    TONGYI_API_KEY = os.getenv('TONGYI_API_KEY')
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = (
        f"{os.getenv('DB_ENGINE')}://"
        f"{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
        f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/"
        f"{os.getenv('DB_NAME')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': int(os.getenv('DB_POOL_SIZE', '5')),
        'pool_recycle': int(os.getenv('DB_POOL_RECYCLE', '3600')),
        'pool_pre_ping': os.getenv('DB_POOL_PRE_PING', 'True').lower() == 'true',
        'connect_args': {
            'connect_timeout': int(os.getenv('DB_CONNECT_TIMEOUT', '5'))
        }
    }

    # 业务配置
    MAX_AGENT_COUNT_PER_USER = int(os.getenv('MAX_AGENT_COUNT_PER_USER', '50'))
    AGENT_EXECUTION_TIMEOUT = int(os.getenv('AGENT_EXECUTION_TIMEOUT', '30'))