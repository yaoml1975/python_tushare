# 项目介绍：基于巴菲特选股策略的量化选股工具 - python_tushare

## 项目概述

本项目是一个基于Python开发的量化投资选股工具，通过调用**Tushare金融数据接口**，实现了沃伦·巴菲特(Warren Buffett)价值投资策略的自动化筛选选股流程。该程序将巴菲特的经典选股原则转化为可量化的指标，通过四个系统化的步骤对A股市场股票进行筛选，帮助投资者发现具有长期投资价值的优质企业。

## 技术架构

### 核心组件

#### 编程语言:
  - Python 3.9.21

#### 数据接口: 
  - Tushare Pro API (需注册获取token)

#### 主要依赖库:（详见:requirements.txt)
  - pandas (数据处理)
  - numpy (数值计算)
  - tushare (金融数据获取)
  - matplotlib/seaborn (可视化)
  - requests (API调用)
  - logging (日志记录)

### 数据源 - Tushare Pro

通过**Tushare Pro**接口获取以下金融数据:**（需申请5000积分的token）**
  - 股票基本信息
  - 财务数据(资产负债表、利润表、现金流量表)
  - 行情数据(日K线、复权因子)
  - 估值指标(PE/PB/PS等)


## 巴菲特选股策略的四步实现

### 股票筛选程序 - tushare_test1.py

#### 功能描述

本程序通过load_or_fetch_stock_basic 获取上市公司基础信息。根据以下规则筛选股票：
  - 排除近两年上市的股票：**(暂未排除)**
  - 排除名称含 "ST" 的股票；
  - 排除代码以 "8" 或 "9" 开头的股票（新三板和 B 股市场）；
  - 排除掉民营企业、外资企业的股票；**(暂未排除)**
  - 仅保留市场类型market为"主板"的股票；**(未选择)**
  - 排除民营企业和外资企业；**(暂未排除)**
  - 仅保留银行；**(未选择)**

保存结果为 tushare_stock_basic_filter_交易日期.csv

#### 输入内容

交易日期：最近一个交易日。可通过工具类stock_utils的函数get_last_trade_date()获取最近一个交易日期。

#### 输出文件和内容

CSV 文件：`tushare_stock_basic_filter1_交易日期.csv`，包含以下字段：
   1. `ts_code`：股票代码。
   2. `name`：股票名称。
   3. `area`：地域。
   4. `industry`：所属行业。
   5. `market`：市场类型。
   6. `list_status`：上市状态。
   7. `list_date`：上市日期。
   8. `is_hs`：是否沪深港通标的。

---

### 股票筛选程序 - tushare_test2.py

#### 功能描述

1. 获取最近交易日期。
2. 读取 `tushare_stock_basic_filter1_交易日期.csv`（基础筛选结果，以下简称 csv1）。
3. 读取 `tushare_daily_交易日期.csv`（日线行情数据，以下简称 csv2）和`tushare_daily_basic_交易日期.csv`（每日指标数据，以下简称 csv3）。
4. 仅合并 `csv1` 中包含的股票，在 `csv2` 和 `csv3` 中对应的数据。
5. 根据以下规则筛选股票：
  - 排除流通市值（circ_mv）大于 1000 亿的股票。**（config.yaml中circ_mv指标定义）**
  - 排除市盈率（pe）小于 5 或大于 50 的股票。**(暂未排除)**
6. 保存筛选结果为 `tushare_stock_basic_filter2_交易日期.csv`。

#### 输入内容

1. 交易日期：最近一个交易日（通过 `get_last_trade_date` 获取）。
2. 输入文件：
  - `tushare_stock_basic_filter1_交易日期.csv`（csv1）。
  - `tushare_daily_交易日期.csv`（csv2）。
  - `tushare_daily_basic_交易日期.csv`（csv3）。

#### 输出文件和内容

CSV 文件：`tushare_stock_basic_filter2_交易日期.csv`，包含以下字段：
  - `ts_code`：股票代码。
  - `name`：股票名称。
  - `area`：地域。
  - `industry`：所属行业。
  - `market`：市场类型。
  - `list_status`：上市状态。
  - `list_date`：上市日期。
  - `is_hs`：是否沪深港通标的。
  - `vol`：成交量。
  - `turnover_rate`：换手率。
  - `pct_chg`：涨跌幅。
  - `circ_mv`：流通市值。
  - `volume_ratio`：量比。

---

### 股票筛选程序 - tushare_test3.py

#### 功能描述

1. 获取最近交易日期。
2. 读取 `tushare_stock_basic_filter2_交易日期.csv` 文件，提取股票信息。
3. 对每只股票，获取其 `list_date`（上市日期），提取年份，并通过`generate_quarter_list(start_year)` 获取从指定年份到当前年份的季度列表。
4. 通过 `fetch_fina_indicator_vip_by_tscode(ts_code, quarter_list, is_save_csv=True)` 获取每只股票的财务数据。
5. 根据以下规则筛选股票：
  - 排除净资产收益率（`roe`）小于4 的股票。**（config.yaml中指定）**
  - 排除净利润增长率（`q_netprofit_yoy`）小于0 的股票。***（config.yaml中指定）**
  - 排除资产负债率（`debt_to_assets`）大于 80股票。***（config.yaml中指定）**
  - 排除企业自由现金流量（`fcff`）为负的股票。**(暂未排除)**
6. 保存筛选结果为 `tushare_stock_basic_filter3_交易日期.csv` 文件。

#### 输出文件和内容

CSV 文件：`tushare_stock_basic_filter3_交易日期.csv` 包含以下字段：
  - `ts_code`：股票代码。
  - `name`：股票名称。
  - `area`：地域。
  - `industry`：所属行业。
  - `market`：市场类型。
  - `list_status`：上市状态。
  - `list_date`：上市日期。
  - `is_hs`：是否沪深港通标的。
  - `vol`：成交量。
  - `turnover_rate`：换手率。
  - `pct_chg`：涨跌幅。
  - `circ_mv`：流通市值。
  - `volume_ratio`：量比。
  - `ann_date`：公告日期。  
  - `end_date`：报告期。  
  - `roe`：净资产收益率。  
  - `fcff`：企业自由现金流量。  
  - `grossprofit_margin`：销售毛利率。  
  - `equity_yoy`：净资产同比增长率。  
  - `debt_to_assets`：资产负债率。  
  - `update_flag`：更新标识。

#### 合并文件功能

1. 使用 `merge_csv_files(file1, file2, output_file)` 合并两个 CSV 文件，保留两个文件中都有的记录。
2. 通过 `ts_code` 列进行合并，合并结果保存为 `tushare_stock_basic_filter3_交易日期_merged.csv` 文件。

---

### 股票筛选程序 - tushare_test4.py

#### 功能描述

1. 获取最近交易日期。
2. 读取 `data/tushare_stock_basic_filter3_交易日期_merged.csv` 文件，提取股票信息。
3. 调用get_recent_kdj_death_cross(ts_code)获取指定股票最近一次 KDJ 死叉的日期。如果发生在近期3个交易之内（get_last_n_trade_dates(n=3)）就排除掉这只股票；
4. 调用get_recent_macd_death_cross(ts_code)获取指定股票最近一次MACD 死叉的日期。如果发生在近期3个交易之内（get_last_n_trade_dates(n=3)）就排除掉这只股票；
5. 根据以下规则筛选股票：
  - 保留成交额i降序排名前6个股票；**（config.yaml中top_volume指定）**
  - 涨幅降序排列的前3名；**（config.yaml中top_pct_chg指定）**
  - 排除掉近3个交易之内 KDJ 死叉的股票；**(暂未加入)**
  - 排除掉近3个交易之内MACD  死叉的股票；**(暂未加入)**
6. 保存筛选结果为 `tushare_stock_basic_filter4_交易日期.csv` 文件。

#### 输入内容

1. 交易日期：最近一个交易日（通过 get_last_trade_date 获取）。
2. 输入文件：tushare_stock_basic_filter3_交易日期_merged.csv（包含财务数据和基本信息的股票列表）。

#### 输出文件和内容

CSV 文件：`tushare_stock_basic_filter4_交易日期.csv` 包含以下字段：
  - `ts_code`：股票代码。
  - `name`：股票名称。
  - `area`：地域。
  - `industry`：所属行业。
  - `market`：市场类型。
  - `list_status`：上市状态。
  - `list_date`：上市日期。
  - `is_hs`：是否沪深港通标的。
  - `vol`：成交量。
  - `turnover_rate`：换手率。
  - `pct_chg`：涨跌幅。
  - `circ_mv`：流通市值。
  - `volume_ratio`：量比。
  - `ann_date`：公告日期。  
  - `end_date`：报告期。  
  - `roe`：净资产收益率。  
  - `fcff`：企业自由现金流量。  
  - `grossprofit_margin`：销售毛利率。  
  - `equity_yoy`：净资产同比增长率。  
  - `debt_to_assets`：资产负债率。  
  - `update_flag`：更新标识。

---


## 相关资源说明

### 工具类stock_utils

```
get_tushare_api()
初始化并返回 Tushare API 对象。
输出: Tushare API 对象。

is_file_older_than(file_path, days=1)
判断文件是否早于指定天数。
输入: file_path (文件路径), days (天数, 默认为 1)。
输出: True 或 False。

get_quarter_end_dates(year)
获取指定年份的季度结束日期。
输入: year (年份)。
输出: 包含季度结束日期的字典。

generate_quarter_list(start_year)
生成从指定年份到当前年份的季度列表。
输入: start_year (起始年份)。
输出: 包含季度信息的列表。

auto_adjust_column_width(file_path)
自动调整 Excel 文件的列宽。
输入: file_path (Excel 文件路径)。
输出: 无（修改文件）。

get_last_trade_date()
获取最近一个交易日的日期。
输出: 最近一个交易日的日期，若无则返回 None。

get_last_n_trade_dates(n=20)
获取最近 n 个交易日的日期。
输入: n (交易日数量, 默认为 20)。
输出: 包含交易日期的列表。

fetch_stock_basic(trade_date, is_save_csv=True)
获取股票基础信息并保存为 CSV 文件。
输入: trade_date (交易日期)。
输出: df（保存为 CSV 文件）。

fetch_daily(trade_date, is_save_csv=True)
获取日线行情数据并保存为 CSV 文件。
输入: trade_date (交易日期)。
输出: df（保存为 CSV 文件）。

fetch_daily_basic(trade_date, is_save_csv=True)
获取每日指标数据并保存为 CSV 文件。
输入: trade_date (交易日期)。
输出: df（保存为 CSV 文件）。

fetch_stk_factor_pro_by_tscode(ts_code, start_date, end_date)
获取指定股票代码在指定日期范围内的股票因子数据。
输入: ts_code (股票代码), start_date (开始日期), end_date (结束日期)。
输出: 股票因子数据的 DataFrame。

ensure_sufficient_data(ts_code, min_days)
确保获取指定股票的足够天数的数据。
输入: ts_code (股票代码), min_days (最小天数)。
输出: 至少 min_days 天的数据的 DataFrame。

get_recent_kdj_death_cross(ts_code)
获取指定股票最近一次 KDJ 死叉的日期。
输入: ts_code (股票代码)。
输出: 最近一次 KDJ 死叉的日期，若无则返回 None。

get_recent_macd_death_cross(ts_code)
获取指定股票最近一次 MACD 死叉的日期。
输入: ts_code (股票代码)。
输出: 最近一次 MACD 死叉的日期，若无则返回 None。

fetch_fina_indicator_vip_by_tscode(ts_code, quarter_list, is_save_csv=True)
获取指定股票的所有财务数据。
输入: ts_code (股票代码)，quarter_list（包含季度信息的列表）。
输出: df（保存为 CSV 文件）。

def fetch_fina_indicator_vip_by_tscode_quarter_str(ts_code, quarter_str, is_save_csv=False)
获取指定股票指定时间的财务数据。
输入: ts_code (股票代码)，quarter_str（包含财报时间字符串）。
输出: df（保存为 CSV 文件）。

```

### API接口返回字段说明

#### 基础信息API接口stock_basic

 - 函数：fetch_stock_basic(trade_date)
 - 描述：可以获取所有上市公司基础信息，调取一次就可以拉取完。
 - 输入：get_last_trade_date获取最近的一个交易日期后，输入参数trade_date，API接口stock_basic获取所有上市公司基础信息。
 - 输出：获取数据后分别写入csv文件，csv文件名后加当前日期，例如：tushare_stock_basic_20250211.csv。
 - csv文件内数据保留字段如下：
```
名称	类型	默认显示	描述
ts_code	str	Y	TS代码
symbol	str	Y	股票代码
name	str	Y	股票名称
area	str	Y	地域
industry	str	Y	所属行业
fullname	str	N	股票全称
enname	str	N	英文全称
cnspell	str	Y	拼音缩写
market	str	Y	市场类型（主板/创业板/科创板/CDR）
exchange	str	N	交易所代码
curr_type	str	N	交易货币
list_status	str	N	上市状态 L上市 D退市 P暂停上市
list_date	str	Y	上市日期
delist_date	str	N	退市日期
is_hs	str	N	是否沪深港通标的，N否 H沪股通 S深股通
act_name	str	Y	实控人名称
act_ent_type	str	Y	实控人企业性质
```

#### 日线行情API接口daily

 - 函数：fetch_daily(trade_date)
 - 描述：本接口是未复权行情，停牌期间不提供数据。只需输入参数trade_date，即可获取所有上市公司日线行情数据。
 - 输入：get_last_20_trade_dates获得最近的20个交易日期列表后，循环输入交易日参数trade_date，API接口daily获取所有上市公司近20个交易日的所有数据。
 - 输出：获取数据后分别写入csv文件，csv文件名后加trade_date交易日期，例如：tushare_daily_20250211.csv。
 - csv文件内数据保留字段如下：
```
名称	类型	描述
ts_code	str	股票代码
trade_date	str	交易日期
open	float	开盘价
high	float	最高价
low	float	最低价
close	float	收盘价
pre_close	float	昨收价【除权价，前复权】
change	float	涨跌额
pct_chg	float	涨跌幅 【基于除权后的昨收计算的涨跌幅：（今收-除权昨收）/除权昨收 】
vol	float	成交量 （手）
amount	float	成交额 （千元）
```

#### 每日指标API接口daily_basic

 - 函数：fetch_daily_basic(trade_date)
 - 描述：可获取全部股票每日重要的基本面指标，可用于选股分析、报表展示等。
 - 输入：get_last_20_trade_dates获得最近的20个交易日期列表后，循环输入交易日参数trade_date，API接口daily_basic获取全部股票近20个交易日的每日重要的基本面指标数据。
 - 输出：获取数据后分别写入csv文件，csv文件名后加trade_date交易日期，例如：tushare_daily_basic_20250211.csv。
 - csv文件内数据保留字段如下：
```
名称	类型	描述
ts_code	str	TS股票代码
trade_date	str	交易日期
close	float	当日收盘价
turnover_rate	float	换手率（%）
turnover_rate_f	float	换手率（自由流通股）
volume_ratio	float	量比
pe	float	市盈率（总市值/净利润， 亏损的PE为空）
pe_ttm	float	市盈率（TTM，亏损的PE为空）
pb	float	市净率（总市值/净资产）
ps	float	市销率
ps_ttm	float	市销率（TTM）
dv_ratio	float	股息率 （%）
dv_ttm	float	股息率（TTM）（%）
total_share	float	总股本 （万股）
float_share	float	流通股本 （万股）
free_share	float	自由流通股本 （万）
total_mv	float	总市值 （万元）
circ_mv	float	流通市值（万元）
```

###  数据初始化程序 - init.py

#### 功能描述
运行init.py主程序，将自动调用get_last_n_trade_dates(n=20)获得最近的20个交易日期列表后，生成3个接口（基础信息API接口stock_basic、日线行情API接口daily、每日指标API接口daily_basic）近20个交易日的csv文件名（tushare_stock_basic_交易日期.csv、tushare_daily_交易日期.csv、tushare_daily_basic_交易日期.csv），并检查是否存在，发现不存在就调用相应接口生成csv文件，依次完成csv数据文件的生成工作。

#### 输入内容
 - get_last_n_trade_dates(n=20)获得最近的20个交易日期

#### 输出内容
 - 生成3个接口（基础信息API接口stock_basic、日线行情API接口daily、每日指标API接口daily_basic）近20个交易日的csv文件（tushare_stock_basic_交易日期.csv、tushare_daily_交易日期.csv、tushare_daily_basic_交易日期.csv）



## 后续开发计划

1. 增加多因子回归分析
2. 实现策略回测框架
3. 开发GUI操作界面
4. 添加国际市场数据支持

## 免责声明

本工具仅供学习交流使用，不构成任何投资建议。股市有风险，投资需谨慎。实际投资决策应考虑更多因素，建议咨询专业投资顾问。

欢迎贡献代码或提出改进建议！


