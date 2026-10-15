"""订单明细：记录商品快照并计算小计。"""

from dataclasses import dataclass


@dataclass(frozen=True)#不允许修改实例属性
class OrderLine:
    product_id: str
    product_name: str
    unit_price_cents: int
    quantity: int

    def __post_init__(self) -> None:
        # 明细可以独立创建，因此也需要校验单价。
        if type(self.unit_price_cents) is not int:
            raise TypeError("订单单价必须为整数分")

        if self.unit_price_cents < 0:
            raise ValueError("订单单价不能为负数")

        # 数量必须为正整数，不能把 True 当成 1 件。
        if type(self.quantity) is not int:
            raise TypeError("购买数量必须为整数")

        if self.quantity <= 0:
            raise ValueError("购买数量必须大于 0")

    def subtotal_cents(self) -> int:
        """返回这一条明细的小计，单位为人民币分。"""
        return self.unit_price_cents * self.quantity