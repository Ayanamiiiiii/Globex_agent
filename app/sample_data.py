"""供本地开发与学习使用的虚构商品数据。"""
"""提供一批虚构商品，暂时不用连接数据库或电商API，也能开发和测试商品相关功能。"""
from app.domain.product import Product


def create_sample_products() -> list[Product]:
    """创建一批样例商品。"""
    # 每次调用都创建新的列表和商品对象。
    return [
        Product(
            product_id="P001",
            name="轻便背包",
            price_cents=19900,
        ),
        Product(
            product_id="P002",
            name="保温杯",
            price_cents=8900,
        ),
        Product(
            product_id="P003",
            name="旅行收纳袋",
            price_cents=3900,
        ),
    ]