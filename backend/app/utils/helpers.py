"""通用辅助函数。"""
from __future__ import annotations

import re
from typing import Any, Iterable, List


def safe_int_id(value: Any) -> int | None:
    """从 Chroma 返回的 id 中安全解析出整数 product_id。

    Chroma 的 id 是字符串，可能带前缀（如 "product_12"）。这里提取其中的数字部分。
    无法解析时返回 None。
    """
    if value is None:
        return None
    if isinstance(value, int):
        return value
    s = str(value).strip()
    if not s:
        return None
    if s.isdigit():
        return int(s)
    # 提取第一段连续数字
    m = re.search(r"\d+", s)
    if not m:
        return None
    return int(m.group(0))


def format_products_for_prompt(products: Iterable[Any]) -> str:
    """将商品对象（ORM 或 dict）格式化为供 LLM 使用的文本块。

    每个商品一行，包含编号、名称、价格、分类、描述。
    """
    lines: List[str] = []
    for idx, p in enumerate(products, start=1):
        name = _attr(p, "name")
        price = _attr(p, "price")
        category = _attr(p, "category")
        description = _attr(p, "description")
        stock = _attr(p, "stock")
        lines.append(
            f"{idx}. 【{name}】 分类:{category} 价格:{price}元 库存:{stock} "
            f"描述:{description}"
        )
    return "\n".join(lines) if lines else "（暂无商品信息）"


def _attr(obj: Any, key: str) -> Any:
    """从对象（属性访问）或字典（键访问）中取值。"""
    if isinstance(obj, dict):
        return obj.get(key, "")
    return getattr(obj, key, "")
