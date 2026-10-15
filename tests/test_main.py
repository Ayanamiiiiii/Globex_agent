"""验证命令行入口。"""

import json

import pytest

import app.__main__ as entry


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
        "当前阶段：本地商品检索",
    ]


def test_main_rejects_negative_budget_without_keyword(monkeypatch, capsys):
    monkeypatch.setattr(entry, "load_local_environment", lambda: None)

    with pytest.raises(SystemExit) as error:
        entry.main(["--max-price-cents", "-1"])

    assert error.value.code == 2
    assert "最高预算不能为负数" in capsys.readouterr().err