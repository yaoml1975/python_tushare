# filename: tushare_test3.py
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
from tqdm import tqdm

from data_cache import dc
from stock_utils import setup_logger, get_last_trade_date, get_quarter_end_dates, \
    fetch_fina_indicator_vip_by_quarter_str
from tushare_test2 import test2

logger = setup_logger()

MAX_WORKERS = 28  # 根据实际网络情况和系统资源调整


def process_stock(row, financial_dict):
    """处理单个股票的财务数据筛选"""
    ts_code = row['ts_code']

    financial_data = financial_dict.get(ts_code)
    if not financial_data:
        return None

    try:
        # 转换为float类型防止类型错误
        roe = float(financial_data['roe'])  # "净资产收益率"
        q_netprofit_yoy = float(financial_data['q_netprofit_yoy'])  # "归属母公司股东的净利润同比增长率(%)(单季度)"
        debt_to_assets = float(financial_data['debt_to_assets'])  # "资产负债率"
    except (ValueError, KeyError) as e:
        logger.debug(f"{ts_code} 财务数据异常: {str(e)}")
        return None

    # 筛选条件:ROE＞=4%、净利润增长率（同比）＞0%、资产负债率＜80%
    if roe >= dc.roe and q_netprofit_yoy > dc.q_netprofit_yoy and debt_to_assets < dc.debt_to_assets:
        # print(f'roe: {roe}, q_netprofit_yoy: {q_netprofit_yoy}, debt_to_assets: {debt_to_assets}')
        return row
    return None


def filter_stocks_by_financials(trade_date, quarter_str):
    """根据财务数据筛选股票（多线程版本）"""
    input_file = os.path.join(dc.filter_dir, f"tushare_stock_basic_filter2_{trade_date}.csv")
    if not os.path.exists(input_file):
        logger.error(f"未找到输入文件: {input_file}，重新生成...")
        test2(trade_date)

    df = pd.read_csv(input_file)
    logger.info(f"初始股票总数: {df.shape[0]}")

    # 获取季度财务数据并建立快速索引
    quarter_financial_data = fetch_fina_indicator_vip_by_quarter_str(quarter_str)
    financial_dict = quarter_financial_data.set_index('ts_code').to_dict('index')

    filtered_stocks = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # 创建任务列表
        tasks = [
            executor.submit(process_stock, row.to_dict(), financial_dict)
            for _, row in df.iterrows()
        ]

        # 使用tqdm显示进度
        with tqdm(total=len(tasks), desc="处理财务数据") as pbar:
            for future in as_completed(tasks):
                result = future.result()
                if result:
                    filtered_stocks.append(result)
                pbar.update(1)

    logger.info(f"符合筛选条件的股票数量: {len(filtered_stocks)}")

    if filtered_stocks:
        result_df = pd.DataFrame(filtered_stocks)
        output_file = os.path.join(dc.filter_dir, f"tushare_stock_basic_filter3_{trade_date}_{quarter_str}.csv")

        # 保留原始列顺序
        result_df = result_df[df.columns.to_list()]

        if os.path.exists(output_file):
            logger.warning(f"筛选结果 CSV 文件已存在： {output_file}")
        else:
            result_df.to_csv(output_file, index=False, encoding="utf-8_sig")
            logger.info(f"筛选结果已保存至 {output_file}")
        return output_file
    else:
        logger.error("未找到符合条件的股票")
        return None


def merge_csv_files(file1, file2, output_file):
    """
    合并两个CSV文件，保留两个文件中都有的记录
    """
    # 读取两个 CSV 文件
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)

    # 打印合并前的记录数量
    logger.info(f"文件 {file1} 的记录数量: {df1.shape[0]}")
    logger.info(f"文件 {file2} 的记录数量: {df2.shape[0]}")

    # 合并两个 CSV 文件，保留两个文件中都有的记录
    merged_df = pd.merge(df1, df2, on='ts_code', how='inner')  # 根据 'ts_code' 列合并

    # 打印合并后的记录数量
    logger.info(f"合并后的记录数量: {merged_df.shape[0]}")

    # 保存合并后的结果
    merged_df.to_csv(output_file, index=False, encoding="utf-8_sig")
    logger.info(f"合并结果已保存至 {output_file}")


def process_quarterly_data(year, quarter_key, last_trade_date):
    """ 处理特定季度的股票筛选逻辑 """
    quarter = get_quarter_end_dates(year)[quarter_key]
    logger.info(f"最近交易日: {last_trade_date}, 财报时间: {quarter}")

    output_file = os.path.join(dc.filter_dir, f"tushare_stock_basic_filter3_{last_trade_date}_{quarter}.csv")
    if os.path.exists(output_file):
        logger.warning(f"csv文件: {output_file} 存在，系统退出！")
        sys.exit(0)

    filter_stocks_by_financials(last_trade_date, quarter)
    return output_file


def test3(last_trade_date):
    try:

        # 处理 2023 Q4
        output_file1 = process_quarterly_data(2023, 'Q4', last_trade_date)

        # 处理 2024 Q3
        output_file2 = process_quarterly_data(2024, 'Q3', last_trade_date)

        # 合并 CSV 文件
        output_file = os.path.join(dc.filter_dir, f"tushare_stock_basic_filter3_{last_trade_date}_merged.csv")
        if os.path.exists(output_file):
            logger.warning(f"csv文件: {output_file} 存在，系统退出！")
            sys.exit(0)

        merge_csv_files(output_file1, output_file2, output_file)

    except KeyboardInterrupt:
        logger.error("检测到手动终止 (Ctrl + C)，程序已安全退出。")
        sys.exit(1)


def main(last_trade_date):
    test3(last_trade_date)


if __name__ == "__main__":
    # 获取最近交易日
    trade_date = get_last_trade_date()
    logger.info(f"当前处理交易日：{trade_date}")

    main(trade_date)
