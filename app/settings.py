"""应用运行配置"""
import os
from pathlib import Path

from dotenv import load_dotenv

def load_local_environment() -> None:
    """加载项目根目录的配置，已有环境变量优先。"""
    env_path = Path(__file__).resolve().parent.parent / ".env" #找到项目根目录下的 .env 文件
    load_dotenv(dotenv_path=env_path, override=False)#读取.env文件后，把配置加载到当前环境变量中，已有的环境变量不覆盖

def is_startup_message_enabled() -> bool:
    """启动信息默认开启，只有字符串1表示开启"""
    return os.getenv("GLOBEX_SHOW_STARTUP","1") == "1"