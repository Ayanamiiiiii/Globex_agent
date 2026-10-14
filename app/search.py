"""商品名称检索。约定：关键词去掉两端空白后，名称包含它就算命中；空关键词和无匹配都返回空列表；结果保留输入顺序."""
"""商品关键词检索。"""

from app.domain.product import Product


def search_products(
    products: list[Product],
    keyword: str,
) -> list[Product]:
    """返回名称包含关键词的商品，保留输入顺序。"""
    keyword = keyword.strip()

    # 空字符串会被视为包含于任何字符串，因此需要提前处理。
    if not keyword:
        return []

    matches = []

    for product in products:
        # 这里的 in 表示字符串包含，例如“杯”包含于“保温杯”。
        if keyword in product.name:
            matches.append(product)

    return matches