"""验证根据商品编号创建订单草稿。"""

from uuid import UUID

import pytest

import app.orders as orders
from app.orders import confirm_order, create_order_draft
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


def test_confirm_order_generates_id_and_preserves_draft(monkeypatch):
    draft = create_order_draft(create_sample_products(), "P001", 2)

    # 固定编号，让测试结果可以重复验证。
    first_uuid = UUID("11111111-1111-4111-8111-111111111111")
    second_uuid = UUID("22222222-2222-4222-8222-222222222222")

    def first_uuid4():
        return first_uuid

    def second_uuid4():
        return second_uuid

    monkeypatch.setattr(orders, "uuid4", first_uuid4)
    first = confirm_order(draft)

    monkeypatch.setattr(orders, "uuid4", second_uuid4)
    second = confirm_order(draft)

    assert first.order_id == first_uuid.hex
    assert second.order_id == second_uuid.hex
    assert first.draft == draft
    assert second.draft == draft
    assert first.total_cents() == 39800
    assert second.total_cents() == 39800


def test_confirm_order_rejects_invalid_draft():
    with pytest.raises(TypeError, match="订单必须关联订单草稿"):
        confirm_order(None)