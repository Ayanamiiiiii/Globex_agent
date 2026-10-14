"""验证商品关键词检索行为。包括正常命中、空白处理、无结果，以及多件商品命中时的顺序"""

import pytest

from app.domain.product import Product
from app.sample_data import create_sample_products
from app.search import search_products


@pytest.mark.parametrize(
    "keyword, expected_ids",
    [
        ("背包", ["P001"]),
        (" 杯 ", ["P002"]),
        ("手机", []),
        ("", []),
        ("   ", []),
    ],
)
def test_search_matches_product_names(keyword, expected_ids):
    products = create_sample_products()

    matches = search_products(products, keyword)

    # 提取结果中的商品编号，方便比较检索结果。
    actual_ids = []
    for product in matches:
        actual_ids.append(product.product_id)
    assert actual_ids == expected_ids


def test_search_preserves_order_and_input_list():
    products = create_sample_products()

    # 故意把 P004 放在最前面，验证结果沿用输入顺序。
    products.insert(
        0,
        Product(
            product_id="P004",
            name="旅行背包",
            price_cents=15900,
        ),
    )
    original_ids = []#记录原始商品编号顺序，验证输入列表未被修改
    for product in products:
        original_ids.append(product.product_id)
    

    matches = search_products(products, "背包")#记录搜索结果，应该命中 P004 和 P001 两件商品

    matches_ids = []
    for product in matches:
        matches_ids.append(product.product_id)
    actual_ids = []
    for product in products:
        actual_ids.append(product.product_id)

    assert matches_ids == ["P004", "P001"]
    assert actual_ids == original_ids