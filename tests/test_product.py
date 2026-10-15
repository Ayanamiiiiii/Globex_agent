"""验证商品价格的类型与范围。"""

import pytest

from app.domain.product import Product


@pytest.mark.parametrize("price_cents", [0, 19900])
def test_product_accepts_valid_price(price_cents):
    product = Product(
        product_id="P001",
        name="轻便背包",
        price_cents=price_cents,
    )

    assert product.price_cents == price_cents


def test_product_rejects_negative_price():
    with pytest.raises(ValueError, match="商品价格不能为负数"):#match内容必须和抛出的异常信息相匹配，否则测试失败
        Product(product_id="P001", name="轻便背包", price_cents=-1)


@pytest.mark.parametrize(
    "price_cents",
    [19900.0, "19900", True, False, None],
)
def test_product_rejects_invalid_price_type(price_cents):
    with pytest.raises(TypeError, match="商品价格必须为整数分"):
        Product(
            product_id="P001",
            name="轻便背包",
            price_cents=price_cents,
        )