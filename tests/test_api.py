"""验证 HTTP 健康检查与商品检索接口。"""

import json

import pytest
from fastapi.testclient import TestClient

import app.api as api

def test_health_returns_ok():
    # 通过 HTTP 路由测试接口，无需预先启动 Uvicorn。
    with TestClient(api.app) as client:
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

@pytest.fixture
def catalog_client(tmp_path, monkeypatch):
    app_dir = tmp_path / "app"
    app_dir.mkdir()
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    rows = [
        {"product_id": "T001", "name": "大背包", "price_cents": 19900},
        {"product_id": "T002", "name": "小背包", "price_cents": 9900},
        {"product_id": "T003", "name": "保温杯", "price_cents": 4900},
        {"product_id": "T004", "name": "赠品背包", "price_cents": 0},
    ]
    (data_dir / "products.json").write_text(
        json.dumps(rows, ensure_ascii=False),
        encoding="utf-8",
    )

    # 使用临时商品文件，并改变当前目录，验证路径定位方式。
    monkeypatch.setattr(api, "__file__", str(app_dir / "api.py"))
    monkeypatch.chdir(app_dir)

    with TestClient(api.app) as client:
        # 将客户端交给测试；测试结束后继续执行，退出 with。
        yield client


@pytest.mark.parametrize(
    "params, expected",
    [
        (
            {"keyword": "背包"},
            [
                {"product_id": "T001", "name": "大背包", "price_cents": 19900},
                {"product_id": "T002", "name": "小背包", "price_cents": 9900},
                {"product_id": "T004", "name": "赠品背包", "price_cents": 0},
            ],
        ),
        (
            {"keyword": "背包", "max_price_cents": 9900},
            [
                {"product_id": "T002", "name": "小背包", "price_cents": 9900},
                {"product_id": "T004", "name": "赠品背包", "price_cents": 0},
            ],
        ),
        (
            {"keyword": "背包", "max_price_cents": 0},
            [
                {"product_id": "T004", "name": "赠品背包", "price_cents": 0},
            ],
        ),
        ({"keyword": ""}, []),
    ],
)
def test_products_search(catalog_client, params, expected):
    response = catalog_client.get("/products", params=params)

    assert response.status_code == 200
    assert response.json() == expected


@pytest.mark.parametrize(
    "params, field",
    [
        ({}, "keyword"),
        ({"keyword": "背包", "max_price_cents": -1}, "max_price_cents"),
        ({"keyword": "背包", "max_price_cents": "abc"}, "max_price_cents"),
    ],
)
def test_products_reject_invalid_query(catalog_client, params, field):
    response = catalog_client.get("/products", params=params)

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["query", field]