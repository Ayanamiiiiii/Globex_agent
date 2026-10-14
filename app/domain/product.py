"""商品领域模型。"""

from dataclasses import dataclass


@dataclass #自动生成初始化方法和便于阅读的对象表示
class Product:# 定义一种商品类型
    """用于在程序中传递一件商品的数据。"""

    product_id: str #商品编号
    name: str  #商品名称
    price_cents: int  # 人民币分，例如 19900 表示 199.00 元。
# 注意：定义 Product 类还没有创建具体商品，调用 Product(...) 才会创建对象。