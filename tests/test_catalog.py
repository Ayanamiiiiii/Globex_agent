"""验证 JSON 商品目录加载。"""

import json

import pytest

from app.catalog import load_products
from app.domain.product import Product


@pytest.mark.parametrize("encoding", ["utf-8", "utf-8-sig"])
def test_load_products_reads_fields_and_preserves_order(tmp_path, encoding):
    path = tmp_path / "products.json"

    # 刻意按逆编号顺序写入，检查加载器是否保留原顺序。
    rows = [
        {"product_id": "P002", "name": "保温杯", "price_cents": 8900},
        {"product_id": "P001", "name": "轻便背包", "price_cents": 19900},
    ]
    path.write_text(
        json.dumps(rows, ensure_ascii=False),
        encoding=encoding,
    )

    products = load_products(path)

    assert products == [
        Product(product_id="P002", name="保温杯", price_cents=8900),
        Product(product_id="P001", name="轻便背包", price_cents=19900),
    ]


def test_load_products_accepts_empty_array(tmp_path):
    path = tmp_path / "products.json"
    path.write_text("[]", encoding="utf-8")

    assert load_products(path) == []


@pytest.mark.parametrize(
    "price_cents, error_type, message",
    [
        (-1, ValueError, "商品价格不能为负数"),
        (19900.0, TypeError, "商品价格必须为整数分"),
    ],
)
def test_load_products_reuses_price_validation(
    tmp_path, price_cents, error_type, message
):
    path = tmp_path / "products.json"
    rows = [
        {
            "product_id": "P001",
            "name": "轻便背包",
            "price_cents": price_cents,
        }
    ]
    path.write_text(
        json.dumps(rows, ensure_ascii=False),
        encoding="utf-8",
    )

    with pytest.raises(error_type, match=message):
        load_products(path)