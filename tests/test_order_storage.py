"""验证订单文件保存和同名文件保护。"""

import json

import pytest

from app.domain.order import Order
from app.order_serialization import order_from_dict
from app.order_storage import save_order
from app.orders import create_order_draft
from app.sample_data import create_sample_products


@pytest.fixture
def sample_order():
    draft = create_order_draft(create_sample_products(), "P001", 2)
    return Order(order_id="O001", draft=draft)


def test_save_order_creates_directory_and_writes_json(tmp_path, sample_order):
    # orders 目录尚不存在，保存函数需要自动创建它。
    path = tmp_path / "orders" / "O001.json"

    save_order(sample_order, path)

    text = path.read_text(encoding="utf-8")
    restored = order_from_dict(json.loads(text))

    assert "轻便背包" in text
    assert restored == sample_order
    assert restored.total_cents() == 39800


def test_save_order_preserves_existing_file(tmp_path, sample_order):
    path = tmp_path / "O001.json"
    original_content = "已有文件内容"
    path.write_text(original_content, encoding="utf-8")

    with pytest.raises(FileExistsError):
        save_order(sample_order, path)

    assert path.read_text(encoding="utf-8") == original_content