"""应用运行配置"""
import os

def is_startup_message_enabled():
    """启动信息默认开启，只有字符串1表示开启"""
    return os.getenv("GLOBEX_SHOW_STARTUP","1") == "1"