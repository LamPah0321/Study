"""Celery 应用实例配置。

使用 Redis 作为 broker 与 backend。autodiscover 自动发现 app.tasks 下的任务。
"""
from __future__ import annotations

from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "ai_mall",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks.indexing"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Shanghai",
    enable_utc=False,
    result_expires=3600,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)

# 自动发现任务模块
celery_app.autodiscover_tasks(["app.tasks"])
