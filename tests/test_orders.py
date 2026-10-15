"""验证根据商品编号创建订单草稿。"""

import pytest

from app.orders import create_order_draft
from app.sample_data import create_sample_products


def test_create_order_draft_uses_selected_product():
    products = create_sample_products()

    # 选择第二件商品，验证函数能够继续向后查找。
    draft = create_order_draft(products, "P002", 2)

    assert len(draft.lines) == 1
    line = draft.lines[0]

    assert line.product_id == "P002"
    assert line.product_name == "保温杯"
    assert line.unit_price_cents == 8900
    assert line.quantity == 2
    assert draft.total_cents() == 17800

    # 与新创建的样例比较，确认原商品目录没有被修改。
    assert products == create_sample_products()


def test_create_order_draft_keeps_price_snapshot():
    products = create_sample_products()

    draft = create_order_draft(products, "P001", 2)

    products[0].name = "新版背包"
    products[0].price_cents = 9900

    assert draft.lines[0].product_name == "轻便背包"
    assert draft.lines[0].unit_price_cents == 19900
    assert draft.total_cents() == 39800


@pytest.mark.parametrize("use_sample_catalog", [False, True])
def test_create_order_draft_rejects_missing_product(use_sample_catalog):
    products = []
    if use_sample_catalog:
        products = create_sample_products()

    with pytest.raises(ValueError, match="未找到指定商品"):
        create_order_draft(products, "P404", 1)


@pytest.mark.parametrize(
    "quantity, error_type, message",
    [
        (0, ValueError, "购买数量必须大于 0"),
        (True, TypeError, "购买数量必须为整数"),
    ],
)
def test_create_order_draft_reuses_quantity_validation(
    quantity, error_type, message
):
    with pytest.raises(error_type, match=message):
        create_order_draft(create_sample_products(), "P001", quantity)