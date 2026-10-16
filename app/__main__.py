'''应用的命令行入口'''
import argparse
from pathlib import Path

from app.order_storage import save_order
from app.orders import confirm_order, create_order_draft
from app.catalog import load_products
from app.search import search_products
from app.settings import is_startup_message_enabled, load_local_environment

def main(argv: list[str] | None = None) -> None:
    '''执行商品检索、草稿预览、订单确认与保存。'''
    parser = argparse.ArgumentParser(description='本地商品检索、草稿预览、订单确认与保存')

    action = parser.add_mutually_exclusive_group()#mutually exclusive 的意思是“互不相容 / 互斥”,也就是说--keyword和--product-id不能同时使用
    action.add_argument('--keyword', help='商品名称关键词')
    action.add_argument('--product-id', help='购买商品的编号')

    parser.add_argument(
        '--max-price-cents',
        type=int,
        help='最高预算（人民币分）',
    )
    parser.add_argument(
        '--quantity',
        type=int,
        help='购买数量，默认 1'
    )
    parser.add_argument(
        '--confirm',
        action='store_true',
        help='确认订单，可配合 --save-order 保存',
    )
    parser.add_argument(
        '--save-order',
        type=Path,
        help='确认后保存订单的 JSON 文件路径',
    )

    args = parser.parse_args(argv)

    # 命令行参数非法时，显示用法并以状态码 2 退出。
    if args.max_price_cents is not None and args.max_price_cents < 0:
        parser.error('最高预算不能为负数')
    if args.quantity is not None and args.product_id is None:
        parser.error('购买数量需要配合商品编号使用')
    if args.product_id is not None and args.max_price_cents is not None:
        parser.error('最高预算只用于关键词检索')
    if args.confirm and args.product_id is None:
        parser.error('确认订单需要配合商品编号使用')
    if args.save_order is not None and not args.confirm:
        parser.error('保存订单需要配合 --confirm 使用')

    load_local_environment()

    if is_startup_message_enabled():
        print('Globex Agent 启动成功！')
        print('当前阶段：商品检索、草稿预览、订单确认与保存')

    # 未提供关键词和商品编号时，保留原来的启动行为。
    if args.keyword is None and args.product_id is None:
        return
    
    # 按入口文件的位置定位商品目录。
    catalog_path = Path(__file__).resolve().parent.parent / 'data' / 'products.json'
    products = load_products(catalog_path)

    #商品数量默认为1，如果用户指定了数量参数，则使用用户指定的数量
    if args.product_id is not None:
        quantity = 1
        if args.quantity is not None:
            quantity = args.quantity


        # 将业务错误转换成命令行提示与退出码 2。
        try:
            #把用户选择的商品编号和数量传给create_order_draft函数，生成订单草稿，只能是一件商品的订单草稿
            draft = create_order_draft(products, args.product_id, quantity)
        except ValueError as error:
            parser.error(str(error))

        print('订单草稿预览')
        for line in draft.lines:
            print(f'{line.product_id} | {line.product_name} | 单价 {line.unit_price_cents} 分 | 数量 {line.quantity}')

        print(f'总金额: {draft.total_cents()} 分')
        if args.confirm:
            # 确认只执行一次，保存和输出使用同一个订单。
            order = confirm_order(draft)

            if args.save_order is not None:
                try:
                    save_order(order, args.save_order)
                except OSError as error:
                    parser.error(f'订单保存失败: {error}')

                print('订单已确认并保存')
                print(f'保存位置: {args.save_order}')
            else:
                print('订单已确认（仅保存在内存中）')

            print(f'订单编号: {order.order_id}')
        return

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