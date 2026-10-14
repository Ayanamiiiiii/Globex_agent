# Globex Agent 学习项目

从零逐步开始搭建跨境电商Agent。

历史阶段；初始化学习仓库、Python虚拟环境的初始化、最小python入口、项目元信息配置、读取启动配置、加载本地配置、配置优先级自动化测试。  
当前阶段：最小商品数据模型  

GLOBEX_SHOW_STARTUP 未设置或为 1 时显示启动信息，为 0 时关闭。  

项目名称、版本、Python 要求与依赖清单记录在 pyproject.toml。  
启动命令：`.\.venv\.Scripts\python.exe -m app`  
测试命令：`.\.venv\Scripts\python.exe -m pytest tests/test_settings.py -q`  

开发环境：Python 3.11，使用uv管理独立的.venv。  

GLOBEX_SHOW_STARTUP 未设置或为 1 时显示启动信息，为 0 时关闭。  
首次使用时，将 .env.example 复制为 .env。
配置优先级：终端环境变量 > .env > 代码默认值。