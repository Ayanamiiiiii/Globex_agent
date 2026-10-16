# Globex Agent 学习项目

从零逐步搭建跨境电商 Agent，按小模块开发、验证和提交。

开发环境：Python 3.11，使用 uv 管理独立的 `.venv`。
项目元信息与依赖以 `pyproject.toml` 为准。

## 当前进度

已完成：

- Python 入口、启动配置和本地 `.env` 加载。
- 商品模型与非负整数分价格校验。
- 固定样例商品与 JSON 商品目录加载。
- 商品名称关键词检索、最高预算筛选。
- 命令行商品检索入口。
- 订单明细模型：商品名称和单价快照、购买数量校验、整数分小计。
- 订单草稿模型：组合一条或多条明细，并按整数分汇总总金额。
- 草稿创建业务流程：按商品编号读取目录价格，创建单商品订单草稿。
- 命令行订单草稿预览，支持商品编号和购买数量。


已支持命令行商品检索与单商品草稿预览，草稿目前保存在内存中。

## 环境准备

以下命令在项目根目录执行。

首次创建虚拟环境；已有可用 `.venv` 时跳过创建：

```powershell
uv venv --python 3.11 .venv
```

安装运行依赖和开发依赖：

```powershell
uv pip install --python .\.venv\Scripts\python.exe -r pyproject.toml --group dev
```

首次使用时，若没有 `.env`，将 `.env.example` 复制为 `.env`。
已有 `.env` 应保留，不提交到 Git。

配置优先级：终端环境变量 > `.env` > 代码默认值。

`GLOBEX_SHOW_STARTUP` 未设置或为 `1` 时显示启动信息，
为其他值时关闭。该开关不影响检索结果与草稿预览输出。

## 本地运行

查看命令行帮助：

```powershell
.\.venv\Scripts\python.exe -m app --help
```

搜索最高预算为 199 元的背包：

```powershell
.\.venv\Scripts\python.exe -m app --keyword 背包 --max-price-cents 19900
```

CLI 从 `data/products.json` 读取商品。

所有金额均使用人民币整数分，`19900` 表示 199 元。
不提供最高预算时不限制价格，预算为 `0` 时只匹配零价商品。
关键词去掉两端空白后进行名称包含匹配；空关键词返回零件商品。

不提供命令行参数时，仅按配置显示启动信息。

```powershell
.\.venv\Scripts\python.exe -m app
```

预览两件商品的订单草稿：

```powershell
.\.venv\Scripts\python.exe -m app --product-id P001 --quantity 2
```

省略 `--quantity` 时默认购买数量为 1。
`--keyword` 与 `--product-id` 不能同时使用。
最高预算用于关键词检索，购买数量用于草稿预览。

## 订单明细

`app/domain/order_line.py` 定义 `OrderLine`。

创建明细时复制商品编号、名称和单价，形成商品快照。
明细禁止普通字段赋值；商品之后改名或调价，不影响已有快照。

- 单价必须为非负整数分。
- 数量必须为正整数，不能使用布尔值。
- `subtotal_cents()` 返回单价乘以数量的小计。

## 订单草稿

`app/domain/order_draft.py` 定义 `OrderDraft`。

草稿使用元组保存至少一条 `OrderLine`，并禁止普通字段赋值。
`total_cents()` 累加所有明细的小计，返回人民币整数分。
零价商品形成的草稿可以具有零元总金额。

单独验证订单草稿：

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_order_draft.py -q
```

当前阶段预期：`8 passed`。

## 创建订单草稿

`app/orders.py` 提供 `create_order_draft(products, product_id, quantity)`。

函数从传入的商品目录中查找编号，使用目录中的名称和单价，
结合购买数量生成一条订单明细，并返回订单草稿。

要求目录内商品编号唯一；找不到商品时抛出 `ValueError`。
当前每次生成一种商品的内存草稿，数量可以为多件。

单独验证草稿创建流程：

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_orders.py -q
```

当前阶段预期：`6 passed`。

## 自动化测试

运行全部测试：

```powershell
.\.venv\Scripts\python.exe -m pytest tests -q
```

当前阶段预期：`65 passed`。

单独验证订单明细：

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_order_line.py -q
```

当前阶段预期：`9 passed`。