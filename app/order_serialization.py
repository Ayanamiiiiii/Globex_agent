"""订单模型与 JSON 兼容字典之间的转换。"""

from app.domain.order import Order
from app.domain.order_draft import OrderDraft
from app.domain.order_line import OrderLine

def order_to_dict(order: Order) -> dict:
    """导出订单编号和明细快照。"""
    lines = []

    for line in order.draft.lines:
        # 创建新的字典，避免导出结果与原订单共享可修改的数据。
        lines.append(
            {
                "product_id": line.product_id,
                "product_name": line.product_name,
                "unit_price_cents": line.unit_price_cents,
                "quantity": line.quantity,
            }
        )

    return {
        "order_id": order.order_id,
        "lines": lines,
    }

def order_from_dict(data: dict) -> Order:
    """根据订单编号和明细快照还原订单。"""
    lines = []

    for row in data["lines"]:
        # 通过模型构造函数，复用单价与数量的校验。
        line = OrderLine(
            product_id=row["product_id"],
            product_name=row["product_name"],
            unit_price_cents=row["unit_price_cents"],
            quantity=row["quantity"],
        )
        lines.append(line)

    # 草稿要求使用元组，并且至少包含一条明细。
    draft = OrderDraft(lines=tuple(lines))

    # 还原已有订单时，沿用保存的编号。
    return Order(order_id=data["order_id"], draft=draft)