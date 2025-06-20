import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()
load_dotenv('.env')

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')

    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@localhost:3307/df'
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 禁用事件系统

    # 添加连接池配置
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 5,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'connect_args': {
            'connect_timeout': 5  # 连接超时设置
        }
    }
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-here')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')

    # 其他配置
    MAX_AGENT_COUNT_PER_USER = 50
    AGENT_EXECUTION_TIMEOUT = 30  # 秒