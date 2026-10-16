"""验证订单导出结构、JSON 兼容性及快照隔离。"""

import json

import pytest

from app.domain.order import Order
from app.domain.order_draft import OrderDraft
from app.domain.order_line import OrderLine
from app.order_serialization import order_to_dict


@pytest.fixture
def sample_order():
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
    return Order(order_id="O001", draft=draft)


def test_order_to_dict_supports_json(sample_order):
    payload = order_to_dict(sample_order)

    assert payload == {
        "order_id": "O001",
        "lines": [
            {
                "product_id": "P001",
                "product_name": "轻便背包",
                "unit_price_cents": 19900,
                "quantity": 2,
            },
            {
                "product_id": "P002",
                "product_name": "保温杯",
                "unit_price_cents": 8900,
                "quantity": 1,
            },
        ],
    }

    # 验证整个结构可以转成 JSON，再还原为相同的数据。
    text = json.dumps(payload, ensure_ascii=False)
    assert json.loads(text) == payload


def test_exported_data_does_not_change_order(sample_order):
    payload = order_to_dict(sample_order)

    # 导出结果可以修改，但原订单快照应该保持不变。
    payload["lines"][0]["unit_price_cents"] = 1
    payload["lines"].clear()

    assert len(sample_order.draft.lines) == 2
    assert sample_order.draft.lines[0].unit_price_cents == 19900
    assert sample_order.total_cents() == 48700