"""验证订单模型。"""

from dataclasses import FrozenInstanceError

import pytest

from app.domain.order import Order
from app.domain.order_draft import OrderDraft
from app.domain.order_line import OrderLine


@pytest.fixture
def sample_draft():
    backpack = OrderLine(
        product_id="P001",
        product_name="轻便背包",
        unit_price_cents=19900,
        quantity=2,
    )
    cup = OrderLine(
        product_id="P002",
        product_name="保温杯",
        unit_price_cents=8900,
        quantity=1,
    )
    return OrderDraft(lines=(backpack, cup))


def test_order_keeps_draft_snapshot(sample_draft):
    order = Order(order_id="O001", draft=sample_draft)

    assert order.order_id == "O001"
    assert order.total_cents() == 48700

    # 禁止在创建后替换订单关联的草稿。
    with pytest.raises(FrozenInstanceError):
        order.draft = None


@pytest.mark.parametrize(
    "order_id, error_type, message",
    [
        ("", ValueError, "订单编号不能为空"),
        ("   ", ValueError, "订单编号不能为空"),
        (None, TypeError, "订单编号必须为字符串"),
        (123, TypeError, "订单编号必须为字符串"),
    ],
)
def test_order_rejects_invalid_id(
    sample_draft, order_id, error_type, message
):
    with pytest.raises(error_type, match=message):
        Order(order_id=order_id, draft=sample_draft)


def test_order_rejects_invalid_draft():
    with pytest.raises(TypeError, match="订单必须关联订单草稿"):
        Order(order_id="O001", draft=None)