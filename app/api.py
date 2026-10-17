"""提供 HTTP 接口的应用入口。"""

from pathlib import Path

from fastapi import FastAPI, Query

from app.catalog import load_products
from app.domain.product import Product
from app.search import search_products

# 创建应用对象；此时还没有启动网络监听。
app = FastAPI()


@app.get("/health")#表示收到访问/health的GET请求时，调用下面的函数，这是一条规则，函数体不会立刻执行
def health() -> dict[str, str]:
    """检查 HTTP 服务是否能够正常响应。"""
    return {"status": "ok"}

@app.get("/products")
def get_products(
    keyword: str,
    max_price_cents: int | None = Query(default=None, ge=0),
) -> list[Product]:
    """按关键词和可选的最高预算检索本地商品。"""
    # 根据当前文件的位置定位商品文件，不依赖终端所在目录。
    catalog_path = Path(__file__).resolve().parent.parent / "data" / "products.json"
    products = load_products(catalog_path)

    # HTTP 接口接收参数，已有业务函数执行商品筛选。
    return search_products(
        products,
        keyword,
        max_price_cents=max_price_cents,
    )