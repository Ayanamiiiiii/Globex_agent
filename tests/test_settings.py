"""验证配置来源之间的优先级。"""

from app import settings


def test_terminal_environment_overrides_dotenv(tmp_path, monkeypatch):
    # 建立临时项目结构，配置加载函数会读取这里的 .env。
    app_dir = tmp_path / "app" 
    app_dir.mkdir()
    (tmp_path / ".env").write_text(
        "GLOBEX_SHOW_STARTUP=0\n", #测试文件里的环境配置为0
        encoding="utf-8",
    )

    # 临时替换模块路径，让配置函数定位到测试目录。
    monkeypatch.setattr(
        settings,
        "__file__",
        str(app_dir / "settings.py"),
    )

    # 文件为 0，终端为 1：终端配置应该优先。
    monkeypatch.setenv("GLOBEX_SHOW_STARTUP", "1")
    settings.load_local_environment()
    assert settings.is_startup_message_enabled() is True

    # 移除终端开关后，重新加载：文件中的 0 应该生效。
    monkeypatch.delenv("GLOBEX_SHOW_STARTUP")
    settings.load_local_environment()
    assert settings.is_startup_message_enabled() is False