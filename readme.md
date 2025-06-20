使用以下命令安装环境和依赖


python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

dify_backend/
├── app/
│   ├── __init__.py         # Flask应用工厂和初始化
│   ├── models.py           # 数据库模型定义
│   ├── routes/
│   │   ├── __init__.py     # 路由包初始化
│   │   ├── agent_routes.py # 智能体相关API路由
│   │   ├── auth_routes.py  # 认证相关API路由
│   │   └── api_routes.py   # API执行相关路由
│   ├── services/
│   │   ├── __init__.py     # 服务层包初始化
│   │   ├── agent_service.py # 智能体业务逻辑
│   │   └── auth_service.py # 认证业务逻辑
│   └── utils/
│       ├── __init__.py     # 工具包初始化
│       ├── auth.py         # 认证相关工具函数
│       └── helpers.py      # 通用辅助函数
├── config.py               # 应用配置
├── requirements.txt        # 依赖列表
└── run.py                  # 应用入口