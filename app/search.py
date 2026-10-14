"""商品名称检索。约定：关键词去掉两端空白后，名称包含它就算命中；空关键词和无匹配都返回空列表；结果保留输入顺序."""
"""给检索增加最高预算，继续使用人民币整数分"""

from app.domain.product import Product


def search_products(
    products: list[Product],
    keyword: str,
    max_price_cents: int | None = None,#传入可以是整数类型也可以不传参数，不传参数的话把None当默认值
) -> list[Product]:
    """返回名称匹配且符合最高预算的商品，保留输入顺序。"""
    """首先判断非空"""
    if max_price_cents is not None:
        #最大价钱得是整数
        if type(max_price_cents) is not int:
            raise TypeError("最高预算必须为整数分")
        #最大价钱必须大于零
        if max_price_cents < 0:
            raise ValueError("最高预算不能为负数")
    
    keyword = keyword.strip()

    # 空字符串会被视为包含于任何字符串，因此需要提前处理。
    if not keyword:
        return []#如果发现是空字符串，直接返回空列表，避免后续的循环和判断

    matches = []

    for product in products:
        # 这里的 in 表示字符串包含，例如“杯”包含于“保温杯”。
        if keyword in product.name:
            if max_price_cents is None or product.price_cents <= max_price_cents:
                matches.append(product)

    return matches