"""验证订单明细。"""

from dataclasses import FrozenInstanceError

import pytest

from app.domain.order_line import OrderLine
from app.domain.product import Product


@pytest.mark.parametrize(
    "unit_price_cents, expected_subtotal",
    [(19900, 39800), (0, 0)],
)
def test_order_line_calculates_subtotal(unit_price_cents, expected_subtotal):
    line = OrderLine(
        product_id="P001",
        product_name="轻便背包",
        unit_price_cents=unit_price_cents,
        quantity=2,
    )

    assert line.subtotal_cents() == expected_subtotal


@pytest.mark.parametrize(
    "quantity, error_type, message",
    [
        (0, ValueError, "购买数量必须大于 0"),
        (-1, ValueError, "购买数量必须大于 0"),
        (True, TypeError, "购买数量必须为整数"),
        (1.5, TypeError, "购买数量必须为整数"),
    ],
)
def test_order_line_rejects_invalid_quantity(quantity, error_type, message):
    with pytest.raises(error_type, match=message):
        OrderLine(
            product_id="P001",
            product_name="轻便背包",
            unit_price_cents=19900,
            quantity=quantity,
        )


@pytest.mark.parametrize(
    "unit_price_cents, error_type, message",
    [
        (-1, ValueError, "订单单价不能为负数"),
        (19900.0, TypeError, "订单单价必须为整数分"),
    ],
)
def test_order_line_rejects_invalid_unit_price(
    unit_price_cents, error_type, message
):
    with pytest.raises(error_type, match=message):
        OrderLine(
            product_id="P001",
            product_name="轻便背包",
            unit_price_cents=unit_price_cents,
            quantity=2,
        )


def test_order_line_keeps_product_snapshot():
    product = Product(
        product_id="P001",
        name="轻便背包",
        price_cents=19900,
    )

    # 复制当前商品字段，而不是把整个商品对象存进明细。
    line = OrderLine(
        product_id=product.product_id,
        product_name=product.name,
        unit_price_cents=product.price_cents,
        quantity=2,
    )

    product.name = "新版背包"
    product.price_cents = 9900

    assert line.product_name == "轻便背包"
    assert line.unit_price_cents == 19900
    assert line.subtotal_cents() == 39800

    # 冻结的明细不允许通过普通赋值修改字段。
    with pytest.raises(FrozenInstanceError):
        line.unit_price_cents = 1