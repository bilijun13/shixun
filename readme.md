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
│       └── auth.py         # 认证相关工具函数
├── config.py               # 应用配置
├── requirements.txt        # 依赖列表
└── run.py                  # 应用入口


sql表创建语句
-- 用户表（核心）
CREATE TABLE `user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(64) NOT NULL,
  `email` varchar(120) NOT NULL,
  `password_hash` varchar(128) NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  `is_admin` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 智能体表（核心业务）
CREATE TABLE `agent` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(128) NOT NULL,
  `description` text,
  `system_prompt` text NOT NULL,
  `model` varchar(64) NOT NULL DEFAULT 'gpt-3.5-turbo',
  `temperature` float NOT NULL DEFAULT '0.7',
  `max_tokens` int NOT NULL DEFAULT '1000',
  `is_public` tinyint(1) NOT NULL DEFAULT '0',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `agents_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 智能体执行记录表（业务日志）
CREATE TABLE `agent_execution` (
  `id` int NOT NULL AUTO_INCREMENT,
  `input` text NOT NULL,
  `output` text,
  `status` varchar(32) NOT NULL DEFAULT 'pending',
  `start_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `end_time` datetime DEFAULT NULL,
  `agent_id` int NOT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `agent_id` (`agent_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `agent_executions_ibfk_1` FOREIGN KEY (`agent_id`) REFERENCES `agents` (`id`) ON DELETE CASCADE,
  CONSTRAINT `agent_executions_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 新增：智能体版本表（扩展功能）
CREATE TABLE `agent_version` (
  `id` int NOT NULL AUTO_INCREMENT,
  `version_name` varchar(64) NOT NULL,
  `config_snapshot` json NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `agent_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `agent_id` (`agent_id`),
  CONSTRAINT `agent_versions_ibfk_1` FOREIGN KEY (`agent_id`) REFERENCES `agents` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;