'''应用的命令行入口'''
from app.settings import is_startup_message_enabled, load_local_environment

def main() ->None:
    '''执行当前阶段的启动行为'''
    load_local_environment()
    
    if is_startup_message_enabled():
        print('Globex Agent 启动成功！')
        print('当前阶段：最小python入口')


if __name__ == '__main__':
    #作为程序运行时调用入口，导入时不自动启动
    main()