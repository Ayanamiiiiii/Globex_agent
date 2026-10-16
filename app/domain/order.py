"""用于承载确认后订单的数据模型。"""

from dataclasses import dataclass

from app.domain.order_draft import OrderDraft


@dataclass(frozen=True)
class Order:
    order_id: str
    draft: OrderDraft

    def __post_init__(self) -> None:
        # 先检查类型，再判断字符串是否为空白。
        if not isinstance(self.order_id, str):
            raise TypeError("订单编号必须为字符串")

        if not self.order_id.strip():
            raise ValueError("订单编号不能为空")

        if not isinstance(self.draft, OrderDraft):
            raise TypeError("订单必须关联订单草稿")

    def total_cents(self) -> int:
        """复用草稿中的总金额，单位为人民币分。"""
        return self.draft.total_cents()