"""将订单模型转换为适合 JSON 保存的数据。"""

from app.domain.order import Order


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