"""种子数据脚本。

向 MySQL 插入示例商品，并为每件商品写入 Chroma 向量索引。

用法：
    python seed_data.py
"""
from __future__ import annotations

import asyncio
import logging
import sys

from sqlalchemy import select

from app.core.database import AsyncSessionLocal, init_db
from app.models.product import Product
from app.services import rag_service

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


# 示例商品：覆盖 数码 / 服饰 / 家居 / 美妆 / 户外 五个分类
SAMPLE_PRODUCTS = [
    {
        "name": "智能蓝牙耳机 Pro",
        "description": "主动降噪真无线蓝牙耳机，支持 LDAC 高清音质，单次续航 8 小时，搭配充电仓可达 32 小时，佩戴舒适稳固。",
        "price": 899.00,
        "category": "数码",
        "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800",
        "stock": 120,
        "specs": {"蓝牙版本": "5.3", "降噪": "主动降噪", "续航": "8h+32h"},
    },
    {
        "name": "4K 高清智能投影仪",
        "description": "家用便携投影仪，1080P 原生分辨率支持 4K 解码，亮度 800ANSI 流明，自动梯形校正，内置智能系统。",
        "price": 2599.00,
        "category": "数码",
        "image": "https://images.unsplash.com/photo-1626379953822-baec19c3accd?w=800",
        "stock": 45,
        "specs": {"分辨率": "1080P/4K解码", "亮度": "800ANSI", "系统": "Android"},
    },
    {
        "name": "纯棉圆领短袖T恤",
        "description": "260g 重磅纯棉面料，柔软透气不变形，简约百搭基础款，男女同款多色可选。",
        "price": 89.00,
        "category": "服饰",
        "image": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=800",
        "stock": 500,
        "specs": {"面料": "100%纯棉", "克重": "260g", "版型": "宽松"},
    },
    {
        "name": "修身直筒牛仔裤",
        "description": "弹力舒适丹宁面料，修身直筒版型修饰腿型，水洗做旧工艺，日常通勤百搭。",
        "price": 269.00,
        "category": "服饰",
        "image": "https://images.unsplash.com/photo-1542272604-787c3835535d?w=800",
        "stock": 200,
        "specs": {"面料": "弹力丹宁", "版型": "修身直筒", "工艺": "水洗做旧"},
    },
    {
        "name": "北欧风实木餐桌",
        "description": "白橡木实木餐桌，1.4米四人位，环保水性漆，稳固桌腿设计，简约北欧风格。",
        "price": 1899.00,
        "category": "家居",
        "image": "https://images.unsplash.com/photo-1577140917170-285929fb55b7?w=800",
        "stock": 30,
        "specs": {"材质": "白橡木", "尺寸": "1.4m", "工艺": "环保水性漆"},
    },
    {
        "name": "记忆棉慢回弹枕",
        "description": "人体工学记忆棉枕头，慢回弹释压，护颈助眠，透气亲肤内套，适合仰睡侧睡。",
        "price": 159.00,
        "category": "家居",
        "image": "https://images.unsplash.com/photo-1630186441797-9d5c5b5b5b5b?w=800",
        "stock": 300,
        "specs": {"材质": "记忆棉", "功能": "护颈助眠", "睡姿": "仰/侧睡"},
    },
    {
        "name": "烟酰胺亮肤精华液",
        "description": "5% 烟酰胺精华，提亮肤色淡化痘印，玻尿酸保湿，清爽不黏腻，敏感肌可用。",
        "price": 199.00,
        "category": "美妆",
        "image": "https://images.unsplash.com/photo-1556228720-195a672e8a03?w=800",
        "stock": 150,
        "specs": {"核心成分": "5%烟酰胺", "功效": "提亮淡印", "肤质": "敏感肌可用"},
    },
    {
        "name": "水润保湿面霜",
        "description": "神经酰胺修护面霜，深层补水锁水，修护肌肤屏障，奶油质地易推开，干皮救星。",
        "price": 129.00,
        "category": "美妆",
        "image": "https://images.unsplash.com/photo-1571781926291-c477ebfd024b?w=800",
        "stock": 180,
        "specs": {"成分": "神经酰胺", "功效": "补水修护", "质地": "奶油质地"},
    },
    {
        "name": "专业户外登山背包 40L",
        "description": "40L 大容量登山包，防泼水耐磨面料，人体工学背负系统减压透气，多仓位分区收纳。",
        "price": 459.00,
        "category": "户外",
        "image": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=800",
        "stock": 80,
        "specs": {"容量": "40L", "面料": "防泼水耐磨", "背负": "减压透气"},
    },
    {
        "name": "速干透气冲锋衣",
        "description": "三合一防风防水冲锋衣，可拆卸内胆，四季适用，登山徒步露营必备，多色可选。",
        "price": 699.00,
        "category": "户外",
        "image": "https://images.unsplash.com/photo-1551488831-00ddcb6c6bd3?w=800",
        "stock": 90,
        "specs": {"类型": "三合一", "功能": "防风防水", "季节": "四季"},
    },
]


async def seed() -> None:
    """插入示例商品并构建向量索引。"""
    logger.info("初始化数据库表...")
    await init_db()

    async with AsyncSessionLocal() as session:
        inserted = 0
        reused = 0
        for item in SAMPLE_PRODUCTS:
            # 按名称去重，避免重复执行时重复插入
            existing = await session.execute(select(Product).where(Product.name == item["name"]))
            product = existing.scalar_one_or_none()
            if product is None:
                product = Product(**item)
                session.add(product)
                await session.commit()
                await session.refresh(product)
                inserted += 1
                logger.info("新增商品: %s (id=%s)", product.name, product.id)
            else:
                reused += 1
                logger.info("商品已存在，跳过: %s (id=%s)", product.name, product.id)

            # 写入 Chroma 向量索引
            text = f"{product.name} {product.category} {product.description}".strip()
            try:
                await rag_service.upsert_product_embedding(product.id, text)
                logger.info("已索引向量: %s", product.name)
            except Exception:
                logger.warning("索引向量失败: %s（可能是未配置 ZHIPU_API_KEY）", product.name, exc_info=True)

        logger.info("完成：新增 %d 件，复用 %d 件", inserted, reused)


def main() -> None:
    try:
        asyncio.run(seed())
    except KeyboardInterrupt:
        logger.info("已中断")
        sys.exit(0)
    except Exception as e:
        logger.error("种子数据脚本执行失败: %s", e, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
