"""将订单保存为 JSON 文件。"""

import json
from pathlib import Path

from app.domain.order import Order
from app.order_serialization import order_to_dict


def save_order(order: Order, path: Path) -> None:
    """将一个订单保存到新文件，已有文件不覆盖。"""
    # 先生成 JSON 文本，转换成功后再操作文件。
    text = json.dumps(order_to_dict(order), ensure_ascii=False, indent=2)

    # 自动创建父目录；目录已存在时继续执行。
    path.parent.mkdir(parents=True, exist_ok=True)

    # x 表示新建文件，目标已存在时抛出 FileExistsError。
    with path.open("x", encoding="utf-8") as file:
        file.write(text + "\n")