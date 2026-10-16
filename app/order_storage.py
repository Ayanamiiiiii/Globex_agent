"""订单 JSON 文件的保存与读取。"""

import json
from pathlib import Path

from app.domain.order import Order
from app.order_serialization import order_from_dict, order_to_dict


def save_order(order: Order, path: Path) -> None:
    """将一个订单保存到新文件，已有文件不覆盖。"""
    # 先生成 JSON 文本，转换成功后再操作文件。
    text = json.dumps(order_to_dict(order), ensure_ascii=False, indent=2)

    # 自动创建父目录；目录已存在时继续执行。
    path.parent.mkdir(parents=True, exist_ok=True)

    # x 表示新建文件，目标已存在时抛出 FileExistsError。
    with path.open("x", encoding="utf-8") as file:
        file.write(text + "\n")

def load_order(path: Path) -> Order:
    """从 JSON 文件读取并还原一个订单。"""
    # utf-8-sig 同时兼容普通 UTF-8 和带 BOM 的 UTF-8 文件。
    with path.open("r", encoding="utf-8-sig") as file:
        data = json.load(file)

    # 字典转为订单对象时，继续执行模型已有的校验。
    return order_from_dict(data)