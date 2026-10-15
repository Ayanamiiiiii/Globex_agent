'''应用的命令行入口'''
import argparse
from pathlib import Path

from app.catalog import load_products
from app.search import search_products
from app.settings import is_startup_message_enabled, load_local_environment

def main(argv: list[str] | None = None) -> None:
    '''执行启动配置及本地商品检索。'''
    parser = argparse.ArgumentParser(description='本地商品检索')
    parser.add_argument('--keyword', help='商品名称关键词')
    parser.add_argument(
        '--max-price-cents',
        type=int,
        help='最高预算（人民币分）',
    )
    args = parser.parse_args(argv)

    # 命令行参数非法时，显示用法并以状态码 2 退出。
    if args.max_price_cents is not None and args.max_price_cents < 0:
        parser.error('最高预算不能为负数')

    load_local_environment()

    if is_startup_message_enabled():
        print('Globex Agent 启动成功！')
        print('当前阶段：本地商品检索')

    # 未提供关键词时，保留原来的启动行为。
    if args.keyword is None:
        return

    # 按入口文件的位置定位商品目录。
    catalog_path = Path(__file__).resolve().parent.parent / 'data' / 'products.json'
    products = load_products(catalog_path)

    matches = search_products(
        products,
        args.keyword,
        max_price_cents=args.max_price_cents,
    )

    print(f'找到 {len(matches)} 件商品')
    for product in matches:
        print(f'{product.product_id} | {product.name} | {product.price_cents} 分')


if __name__ == '__main__':
    #作为程序运行时调用入口，导入时不自动启动
    main()