"""创建订单草稿的业务流程。"""

from app.domain.order_draft import OrderDraft
from app.domain.order_line import OrderLine
from app.domain.product import Product


def create_order_draft(
    products: list[Product],
    product_id: str,
    quantity: int,
) -> OrderDraft:
    """根据商品编号和数量，创建单商品订单草稿。"""
    """只负责把用户当前点选的那1件商品包装成明细（line），然后生成一张只有 1 行明细的初始订单草稿"""
    for product in products:
        #在大仓库里只要目标目标编号一致的商品
        if product.product_id == product_id:
            # 使用目录中的名称和单价，形成明细快照。
            # 数量是否合法，由 OrderLine 继续校验。
            line = OrderLine(
                product_id=product.product_id,
                product_name=product.name,
                unit_price_cents=product.price_cents,
                quantity=quantity,
            )

            return OrderDraft(lines=(line,))

    # 遍历全部商品后仍未匹配，才报告找不到商品。
    raise ValueError("未找到指定商品")