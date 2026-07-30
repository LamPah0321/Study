"""应用配置模块。

通过 pydantic-settings 从 .env 文件读取配置项。
"""
from __future__ import annotations

from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """全局配置，读取自同目录下的 .env 文件。"""

    # 数据库（MySQL 8 + aiomysql 异步驱动）
    DATABASE_URL: str = "mysql+aiomysql://root:root@localhost:3306/ai_mall"

    # Redis（缓存 + Celery broker）
    REDIS_URL: str = "redis://localhost:6379/0"

    # 智谱 AI（GLM-4.5-Air + embedding-3）
    ZHIPU_API_KEY: str = ""
    LLM_MODEL: str = "glm-4.5-air"
    EMBEDDING_MODEL: str = "embedding-3"

    # Chroma 向量库（嵌入式）
    CHROMA_COLLECTION: str = "product_embeddings"
    CHROMA_PATH: str = "./chroma_data"

    # CORS 允许的前端来源
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # 应用基础信息
    APP_TITLE: str = "AI Mall API"
    APP_VERSION: str = "1.0.0"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


# 单例配置对象
settings = Settings()
