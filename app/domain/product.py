"""商品领域模型。"""

from dataclasses import dataclass

# 注意：定义 Product 类还没有创建具体商品，调用 Product(...) 才会创建对象。

@dataclass #自动生成初始化方法和便于阅读的对象表示
class Product:# 定义一种商品类型
    """用于在程序中传递一件商品的数据。"""
    product_id: str #商品编号
    name: str  #商品名称
    price_cents: int  # 人民币分，例如 19900 表示 199.00 元。
    #追加规则输入的价格必须是整数，且大于等于0
    def __post_init__(self) -> None:#@datacalss自动生成的__init__方法会在对象创建后调用__post_init__方法
        # 类型注解不会自动检查输入，因此这里主动校验。
        if type(self.price_cents) is not int:
            raise TypeError("商品价格必须为整数分")

        if self.price_cents < 0:
            raise ValueError("商品价格不能为负数")