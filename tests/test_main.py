"""验证命令行入口。"""

import json

import pytest

import app.__main__ as entry
from app.sample_data import create_sample_products
from app.domain.order import Order
from app.orders import confirm_order, create_order_draft
from app.order_storage import load_order, save_order

def test_main_searches_catalog_with_budget(tmp_path, monkeypatch, capsys):
    app_dir = tmp_path / "app"
    app_dir.mkdir()
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    rows = [
        {"product_id": "T001", "name": "大背包", "price_cents": 19900},
        {"product_id": "T002", "name": "小背包", "price_cents": 9900},
        {"product_id": "T003", "name": "保温杯", "price_cents": 4900},
    ]
    (data_dir / "products.json").write_text(
        json.dumps(rows, ensure_ascii=False),
        encoding="utf-8",
    )

    # 模拟入口位置，并隔离本机 .env 配置。
    monkeypatch.setattr(entry, "__file__", str(app_dir / "__main__.py"))
    monkeypatch.setattr(entry, "load_local_environment", lambda: None)
    monkeypatch.setenv("GLOBEX_SHOW_STARTUP", "0")

    # 改变当前目录，检查商品路径是否根据入口位置定位。
    monkeypatch.chdir(app_dir)

    entry.main(["--keyword", "背包", "--max-price-cents", "15000"])

    assert capsys.readouterr().out.splitlines() == [
        "找到 1 件商品",
        "T002 | 小背包 | 9900 分",
    ]


def test_main_without_keyword_only_shows_startup(tmp_path, monkeypatch, capsys):
    # 此临时位置没有商品文件；无关键词启动应当正常完成。
    monkeypatch.setattr(
        entry, "__file__", str(tmp_path / "app" / "__main__.py")
    )
    monkeypatch.setattr(entry, "load_local_environment", lambda: None)#不读取本机 .env 配置
    monkeypatch.setenv("GLOBEX_SHOW_STARTUP", "1")

    entry.main([])

    assert capsys.readouterr().out.splitlines() == [
        "Globex Agent 启动成功！",
        "当前阶段：商品检索、草稿预览、订单确认及文件读写",
    ]


def test_main_rejects_negative_budget_without_keyword(monkeypatch, capsys):
    monkeypatch.setattr(entry, "load_local_environment", lambda: None)

    with pytest.raises(SystemExit) as error:
        entry.main(["--max-price-cents", "-1"])

    assert error.value.code == 2
    assert "最高预算不能为负数" in capsys.readouterr().err

@pytest.fixture
def preview_cli(monkeypatch):
    """准备独立的预览测试环境。"""
    monkeypatch.setattr(entry, "load_local_environment", lambda: None)
    monkeypatch.setattr(
        entry, "load_products", lambda _path: create_sample_products()
    )
    monkeypatch.setenv("GLOBEX_SHOW_STARTUP", "0")

    # 默认禁止写文件，文件保存测试会单独启用真实保存函数。
    def unexpected_save(_order, _path):
        pytest.fail("本测试不应保存订单")

    monkeypatch.setattr(entry, "save_order", unexpected_save)


@pytest.mark.parametrize(
    "arguments, quantity, total",
    [
        (["--product-id", "P001"], 1, 19900),
        (["--product-id", "P001", "--quantity", "2"], 2, 39800),
    ],
)
def test_main_previews_order_draft(
    preview_cli, monkeypatch, capsys, arguments, quantity, total
):
    def unexpected_confirmation(_draft):
        pytest.fail("草稿预览不应确认订单")

    monkeypatch.setattr(entry, "confirm_order", unexpected_confirmation)

    entry.main(arguments)

    # 同时检查：预览不会确认订单，输出的商品、数量和金额正确。
    assert capsys.readouterr().out.splitlines() == [
        "订单草稿预览",
        f"P001 | 轻便背包 | 单价 19900 分 | 数量 {quantity}",
        f"总金额: {total} 分",
    ]


@pytest.mark.parametrize(
    "arguments, message",
    [
        (
            ["--product-id", "P001", "--quantity", "0"],
            "购买数量必须大于 0",
        ),
        (
            ["--product-id", "P001", "--quantity", "-1"],
            "购买数量必须大于 0",
        ),
        (["--product-id", "P404"], "未找到指定商品"),
        (
            ["--keyword", "背包", "--product-id", "P001"],
            "--product-id",
        ),
        (["--quantity", "2"], "购买数量需要配合商品编号使用"),
        (
            ["--product-id", "P001", "--max-price-cents", "100"],
            "最高预算只用于关键词检索",
        ),
    ],
)
def test_main_rejects_invalid_preview_arguments(
    preview_cli, capsys, arguments, message
):
    with pytest.raises(SystemExit) as error:
        entry.main(arguments)

    assert error.value.code == 2
    assert message in capsys.readouterr().err

@pytest.mark.parametrize(
    "arguments, quantity, total",
    [
        (["--product-id", "P001", "--confirm"], 1, 19900),
        (
            ["--product-id", "P001", "--quantity", "2", "--confirm"],
            2,
            39800,
        ),
    ],
)
def test_main_confirms_order(
    preview_cli, monkeypatch, capsys, arguments, quantity, total
):
    confirmed_drafts = []

    def fake_confirm_order(draft):
        # 记录传入的草稿，并固定编号，让输出可以稳定验证。
        confirmed_drafts.append(draft)
        return Order(order_id="TEST-ORDER-001", draft=draft)

    monkeypatch.setattr(entry, "confirm_order", fake_confirm_order)

    entry.main(arguments)

    assert len(confirmed_drafts) == 1
    assert confirmed_drafts[0].lines[0].quantity == quantity
    assert confirmed_drafts[0].total_cents() == total
    assert capsys.readouterr().out.splitlines() == [
        "订单草稿预览",
        f"P001 | 轻便背包 | 单价 19900 分 | 数量 {quantity}",
        f"总金额: {total} 分",
        "订单已确认（仅保存在内存中）",
        "订单编号: TEST-ORDER-001",
    ]


@pytest.mark.parametrize(
    "arguments",
    [
        ["--confirm"],
        ["--keyword", "背包", "--confirm"],
    ],
)
def test_main_rejects_confirmation_without_product(
    preview_cli, monkeypatch, capsys, arguments
):
    def unexpected_call(_value):
        pytest.fail("参数非法时不应读取商品或确认订单")

    monkeypatch.setattr(entry, "load_products", unexpected_call)
    monkeypatch.setattr(entry, "confirm_order", unexpected_call)

    with pytest.raises(SystemExit) as error:
        entry.main(arguments)

    assert error.value.code == 2
    assert "确认订单需要配合商品编号使用" in capsys.readouterr().err

def test_main_saves_confirmed_order(preview_cli, tmp_path, monkeypatch, capsys):
    path = tmp_path / "orders" / "O001.json"
    confirmed_orders = []

    def tracked_confirm_order(draft):
        # 记录实际确认出来的订单，检查保存的是同一份数据。
        order = confirm_order(draft)
        confirmed_orders.append(order)
        return order

    monkeypatch.setattr(entry, "confirm_order", tracked_confirm_order)
    monkeypatch.setattr(entry, "save_order", save_order)

    entry.main([
        "--product-id", "P001",
        "--quantity", "2",
        "--confirm",
        "--save-order", str(path),
    ])

    assert len(confirmed_orders) == 1
    restored = load_order(path)
    assert restored == confirmed_orders[0]
    assert restored.total_cents() == 39800
    assert capsys.readouterr().out.splitlines() == [
        "订单草稿预览",
        "P001 | 轻便背包 | 单价 19900 分 | 数量 2",
        "总金额: 39800 分",
        "订单已确认并保存",
        f"保存位置: {path}",
        f"订单编号: {restored.order_id}",
    ]


@pytest.mark.parametrize(
    "arguments",
    [
        ["--save-order", "order.json"],
        ["--product-id", "P001", "--save-order", "order.json"],
    ],
)
def test_main_requires_confirmation_for_save(
    preview_cli, monkeypatch, capsys, arguments
):
    def unexpected_catalog_load(_path):
        pytest.fail("参数非法时不应读取商品目录")

    monkeypatch.setattr(entry, "load_products", unexpected_catalog_load)

    with pytest.raises(SystemExit) as error:
        entry.main(arguments)

    assert error.value.code == 2
    assert "保存订单需要配合 --confirm 使用" in capsys.readouterr().err


def test_main_preserves_existing_order_file(
    preview_cli, tmp_path, monkeypatch, capsys
):
    path = tmp_path / "existing.json"
    original_content = "已有订单内容"
    path.write_text(original_content, encoding="utf-8")
    monkeypatch.setattr(entry, "save_order", save_order)

    with pytest.raises(SystemExit) as error:
        entry.main([
            "--product-id", "P001",
            "--confirm",
            "--save-order", str(path),
        ])

    captured = capsys.readouterr()
    assert error.value.code == 2
    assert "订单保存失败" in captured.err
    assert "订单已确认" not in captured.out
    assert path.read_text(encoding="utf-8") == original_content


def test_main_reports_order_save_error(
    preview_cli, tmp_path, monkeypatch, capsys
):
    path = tmp_path / "denied.json"

    def fail_save(_order, _path):
        raise PermissionError("模拟写入被拒绝")

    monkeypatch.setattr(entry, "save_order", fail_save)

    with pytest.raises(SystemExit) as error:
        entry.main([
            "--product-id", "P001",
            "--confirm",
            "--save-order", str(path),
        ])

    captured = capsys.readouterr()
    assert error.value.code == 2
    assert "订单保存失败" in captured.err
    assert "模拟写入被拒绝" in captured.err
    assert "订单已确认" not in captured.out
    assert not path.exists()


def test_main_loads_saved_order(preview_cli, tmp_path, monkeypatch, capsys):
    draft = create_order_draft(create_sample_products(), "P001", 2)
    saved_order = Order(order_id="SAVED-ORDER-001", draft=draft)
    path = tmp_path / "saved.json"
    save_order(saved_order, path)
    original_bytes = path.read_bytes()

    def unexpected_operation(_value):
        pytest.fail("读取订单不应加载商品目录或确认新订单")

    monkeypatch.setattr(entry, "load_products", unexpected_operation)
    monkeypatch.setattr(entry, "confirm_order", unexpected_operation)

    entry.main(["--load-order", str(path)])

    assert capsys.readouterr().out.splitlines() == [
        "已保存订单",
        "订单编号: SAVED-ORDER-001",
        "P001 | 轻便背包 | 单价 19900 分 | 数量 2",
        "总金额: 39800 分",
    ]
    assert path.read_bytes() == original_bytes


@pytest.mark.parametrize(
    "extra",
    [
        ["--keyword", "背包"],
        ["--product-id", "P001"],
        ["--max-price-cents", "0"],
        ["--quantity", "2"],
        ["--confirm"],
        ["--save-order", "new.json"],
    ],
)
def test_main_rejects_load_order_conflicts(
    preview_cli, monkeypatch, capsys, extra
):
    def unexpected_load(_path):
        pytest.fail("参数冲突时不应读取订单")

    monkeypatch.setattr(entry, "load_order", unexpected_load)

    with pytest.raises(SystemExit) as error:
        entry.main(["--load-order", "saved.json"] + extra)

    captured = capsys.readouterr()
    assert error.value.code == 2
    assert captured.err
    if "--confirm" in extra:
        assert "读取订单不能同时使用预算、数量、确认或保存参数" in captured.err


@pytest.mark.parametrize(
    "failure",
    [
        FileNotFoundError("模拟订单文件不存在"),
        ValueError("购买数量必须大于 0"),
        TypeError("订单单价必须为整数分"),
        KeyError("quantity"),
    ],
)
def test_main_reports_order_load_error(
    preview_cli, monkeypatch, capsys, failure
):
    def fail_load(_path):
        raise failure

    monkeypatch.setattr(entry, "load_order", fail_load)

    with pytest.raises(SystemExit) as error:
        entry.main(["--load-order", "saved.json"])

    captured = capsys.readouterr()
    assert error.value.code == 2
    assert "订单读取失败" in captured.err
    assert str(failure) in captured.err
    assert "已保存订单" not in captured.out