"""从 JSON 文件读取商品目录。"""

import json
from pathlib import Path

from app.domain.product import Product


def load_products(path: Path) -> list[Product]:
    """读取约定格式的商品数组，创建商品对象。"""
    # utf-8-sig 兼容普通 UTF-8 和带 BOM 的 UTF-8 文件。
    # with 确保读取结束或发生异常时，文件都会关闭。
    with path.open("r", encoding="utf-8-sig") as file:
        rows = json.load(file)

    products = []

    for row in rows:
        # 字典中的字段转换为商品对象，自动触发价格校验。
        product = Product(
            product_id=row["product_id"],
            name=row["name"],
            price_cents=row["price_cents"],
        )
        products.append(product)

    return products