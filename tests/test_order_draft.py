"""验证订单草稿。"""

from dataclasses import FrozenInstanceError

import pytest

from app.domain.order_draft import OrderDraft
from app.domain.order_line import OrderLine


@pytest.mark.parametrize(
    "unit_price_cents, expected_total",
    [(19900, 39800), (0, 0)],
)
def test_order_draft_totals_single_line(unit_price_cents, expected_total):
    line = OrderLine(
        product_id="P001",
        product_name="轻便背包",
        unit_price_cents=unit_price_cents,
        quantity=2,
    )

    draft = OrderDraft(lines=(line,))

    assert draft.total_cents() == expected_total


def test_order_draft_totals_multiple_lines():
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

    draft = OrderDraft(lines=(backpack, cup))

    assert draft.total_cents() == 48700


def test_order_draft_rejects_empty_lines():
    with pytest.raises(ValueError, match="订单草稿至少需要一条明细"):
        OrderDraft(lines=())


def test_order_draft_rejects_mutable_list():
    line = OrderLine(
        product_id="P001",
        product_name="轻便背包",
        unit_price_cents=19900,
        quantity=2,
    )

    # 故意传入列表，检查运行时校验。
    with pytest.raises(TypeError, match="订单草稿明细必须使用元组"):
        OrderDraft(lines=[line])


@pytest.mark.parametrize("invalid_line", [None, "P001"])
def test_order_draft_rejects_invalid_member(invalid_line):
    line = OrderLine(
        product_id="P001",
        product_name="轻便背包",
        unit_price_cents=19900,
        quantity=2,
    )

    # 非法元素放在合法明细后，检查是否逐项验证。
    with pytest.raises(TypeError, match="订单草稿中的每一项必须是订单明细"):
        OrderDraft(lines=(line, invalid_line))


def test_order_draft_rejects_replacing_lines():
    line = OrderLine(
        product_id="P001",
        product_name="轻便背包",
        unit_price_cents=19900,
        quantity=2,
    )
    draft = OrderDraft(lines=(line,))

    with pytest.raises(FrozenInstanceError):
        draft.lines = ()