"""提供 HTTP 接口的应用入口。"""

from fastapi import FastAPI

# 创建应用对象；此时还没有启动网络监听。
app = FastAPI()


@app.get("/health")#表示收到访问/health的GET请求时，调用下面的函数，这是一条规则，函数体不会立刻执行
def health() -> dict[str, str]:
    """检查 HTTP 服务是否能够正常响应。"""
    return {"status": "ok"}