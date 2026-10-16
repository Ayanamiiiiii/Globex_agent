"""验证订单文件读写及文件保护。"""

import json

import pytest

from app.domain.order import Order
from app.order_serialization import order_to_dict
from app.order_storage import load_order, save_order              
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
    restored = load_order(path)

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


@pytest.mark.parametrize("encoding", ["utf-8", "utf-8-sig"])
def test_load_order_accepts_utf8_files(tmp_path, sample_order, encoding):
    path = tmp_path / "O001.json"
    text = json.dumps(order_to_dict(sample_order), ensure_ascii=False)
    path.write_text(text, encoding=encoding)

    restored = load_order(path)

    assert restored == sample_order
    assert restored.total_cents() == 39800


def test_load_order_rejects_missing_file(tmp_path):
    path = tmp_path / "missing.json"

    with pytest.raises(FileNotFoundError):
        load_order(path)

    assert not path.exists()


def test_load_order_rejects_invalid_json(tmp_path):
    path = tmp_path / "broken.json"
    path.write_text("{", encoding="utf-8")

    with pytest.raises(json.JSONDecodeError):
        load_order(path)


def test_load_order_reuses_model_validation(tmp_path, sample_order):
    path = tmp_path / "invalid.json"
    data = order_to_dict(sample_order)
    data["lines"][0]["quantity"] = 0
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    with pytest.raises(ValueError, match="购买数量必须大于 0"):
        load_order(path)