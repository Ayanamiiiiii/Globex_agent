"""验证 HTTP 健康检查接口。"""

from fastapi.testclient import TestClient

from app.api import app


def test_health_returns_ok():
    # 通过 HTTP 路由测试接口，无需预先启动 Uvicorn。
    with TestClient(app) as client:
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}