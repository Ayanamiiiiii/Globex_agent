"""订单草稿：组合订单明细并计算总金额。"""

from dataclasses import dataclass

from app.domain.order_line import OrderLine


@dataclass(frozen=True)
class OrderDraft:
    lines: tuple[OrderLine, ...]

    def __post_init__(self) -> None:
        # 使用元组，避免通过列表增删改变已有草稿。
        if not isinstance(self.lines, tuple):
            raise TypeError("订单草稿明细必须使用元组")

        if not self.lines:
            raise ValueError("订单草稿至少需要一条明细")

        # 类型注解不会自动检查元素，需要逐项验证。
        for line in self.lines:
            if not isinstance(line, OrderLine):
                raise TypeError("订单草稿中的每一项必须是订单明细")

    def total_cents(self) -> int:
        """累加所有明细的小计，单位为人民币分。"""
        total = 0

        for line in self.lines:
            total += line.subtotal_cents()

        return total