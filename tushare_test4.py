# filename: tushare_test4.py

import os
import sys

import pandas as pd

from data_cache import dc
from stock_utils import setup_logger, fetch_weekly, get_quarter_end_dates, auto_adjust_column_width, get_last_trade_date
from tushare_test3 import test3

logger = setup_logger()


def filter_stocks_by_weekly(trade_date):
    """根据财务数据筛选股票"""
    try:
        output_file = os.path.join(dc.filter_dir, f"tushare_stock_basic_filter4_{trade_date}.csv")
        if os.path.exists(output_file):
            logger.warning(f"筛选结果 CSV 文件已存在： {output_file}, 系统退出！")
            sys.exit(0)

        # 输入文件 csv1 和周报数据 csv2 文件路径
        quarter_list = get_quarter_end_dates(dc.period_year)
        quarter_end_date = quarter_list[dc.period_quarter]
        filename = f"tushare_stock_basic_filter3_{trade_date}_{quarter_end_date}.csv"
        input_file = os.path.join(dc.filter_dir, filename)
        if not os.path.exists(input_file):
            logger.error(f"未找到输入文件: {input_file}，重新生成...")
            test3(trade_date)

        # 获取周报数据 csv2
        weekly_data = fetch_weekly(trade_date)
        weekly_df = pd.DataFrame(weekly_data)
        if weekly_df.shape[0] == 0:
            logger.error(f"周报 {trade_date} 数据为 {weekly_df.shape[0]}, 请确认API接口！")
            return None
        logger.info(f"周报 {trade_date} 获取股票总数: {weekly_df.shape[0]}")

        # 读取输入文件 csv1
        df = pd.read_csv(input_file)
        logger.info(f"初始股票总数: {df.shape[0]}")

        # 合并 csv1 和 csv2，基于 ts_code 进行合并
        # 只保留 df 和 weekly_df 中 ts_code 都存在的行。
        # 如果某个 ts_code 在 df 中存在但在 weekly_df 中不存在（或反之），则该行会被丢弃。
        merged_df = pd.merge(df, weekly_df, on='ts_code', how='inner')
        logger.info(f"合并后的股票数量: {merged_df.shape[0]}")

        # 筛选周成交额前6名的股票
        merged_df['amount'] = merged_df['amount'].astype(float)
        sorted_by_vol = merged_df.sort_values(by='amount', ascending=False)
        sorted_by_vol['volume_rank'] = sorted_by_vol['amount'].rank(method='min', ascending=False).astype(int)  # 正确排名
        # top_volume = sorted_by_vol.head(6)
        top_volume = sorted_by_vol.head(dc.top_volume)
        logger.info(f"筛选后成交额前6名的股票数量: {top_volume.shape[0]}")

        # 打印成交额排名的股票
        logger.info("按成交额降序排列的前6名股票：")
        logger.info(top_volume[['ts_code', 'name', 'amount', 'volume_rank']])

        # 筛选周涨幅前3名的股票
        merged_df['pct_chg'] = merged_df['pct_chg'].astype(float)
        sorted_by_pct_chg = merged_df.sort_values(by='pct_chg', ascending=False)
        sorted_by_pct_chg['pct_rank'] = sorted_by_pct_chg['pct_chg'].rank(method='min', ascending=False).astype(
            int)  # 正确排名
        # top_pct_chg = sorted_by_pct_chg.head(3)
        top_pct_chg = sorted_by_pct_chg.head(dc.top_pct_chg)
        logger.info(f"筛选后涨幅前3名的股票数量: {top_pct_chg.shape[0]}")

        # 打印涨幅排名的股票
        logger.info("按涨幅降序排列的前3名股票：")
        logger.info(top_pct_chg[['ts_code', 'name', 'pct_chg', 'pct_rank']])

        # 为成交额排名和涨幅排名分别标注排名类型
        top_volume = top_volume.copy()
        top_volume.loc[:, 'rank'] = top_volume['volume_rank'].apply(lambda x: f"周成交额排名 {x}")

        top_pct_chg = top_pct_chg.copy()
        top_pct_chg.loc[:, 'rank'] = top_pct_chg['pct_rank'].apply(lambda x: f"周涨幅排名 {x}")

        # filds = ['ts_code', 'name', 'area', 'industry', 'market', 'list_date', 'act_name',
        #          'act_ent_type', 'pct_chg', 'amount', 'trade_date_x', 'circ_mv', 'pe',
        #          'rank']

        filds = ['ts_code', 'name', 'trade_date_x', 'rank', 'area', 'industry', 'market', 'pe']

        # 合并成交额前6名和涨幅前3名的股票
        final_stocks = pd.concat([top_volume[filds],
                                  top_pct_chg[filds]]).drop_duplicates(subset='ts_code', keep='first')

        # 只保留指定的列
        final_stocks = final_stocks[filds]

        logger.info(f"最终筛选后的股票数量: {final_stocks.shape[0]}")

        # 保存筛选结果
        if final_stocks.shape[0] > 0:
            final_stocks.to_csv(output_file, index=False, encoding="utf-8_sig")
            logger.info(f"筛选结果已保存至 {output_file}")
            return output_file
        else:
            logger.error("未找到符合条件的股票")
            return None
    except KeyboardInterrupt:
        logger.error("检测到手动终止 (Ctrl + C)，程序已安全退出。")
        sys.exit(1)


def test4(last_trade_date):
    # 筛选周累计成交额排名前6的股票和选取当周涨幅排名前3的股票
    return filter_stocks_by_weekly(last_trade_date)


def main(last_trade_date):
    return test4(last_trade_date)


def merge_csv(files, output_path):
    # 读取第一个文件，保留表头
    first_file = pd.read_csv(files[0])

    # 读取其他文件，跳过表头
    dfs = [first_file]  # 从第一个文件开始

    for file in files[1:]:
        # 跳过后续文件的表头，header=None
        dfs.append(pd.read_csv(file, header=0))  # header=0 跳过表头

    # 合并所有文件
    merged_df = pd.concat(dfs, ignore_index=True)

    # 保存合并后的结果，保留表头（只会有一个表头）
    merged_df.to_csv(output_path, index=False, header=True, encoding="utf-8_sig")

    return merged_df


def save_to_excel(df, excel_path, sheet_name="Sheet1"):
    # 设置中文表头（假设原表头是英文，需要替换）
    columns_mapping = {
        "ts_code": "股票代码",
        "name": "股票名称",
        "trade_date_x": "交易日期",
        "rank": "排名方式",
        "area": "区域",
        "industry": "行业",
        "market": "板块",
        "pe": "市盈率",
        # 可以继续映射其他列
    }

    # 替换表头为中文
    df.rename(columns=columns_mapping, inplace=True)

    # 保存到 Excel 文件
    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)

    auto_adjust_column_width(excel_path)
    print(f"数据已成功保存到 Excel 文件: {excel_path}")


if __name__ == "__main__":
    # friday_trade_dates = get_friday_trade_dates(2025, 2)
    #
    # # 用于存储临时生成的 CSV 文件路径
    # temp_files = []
    #
    # for trade_date in friday_trade_dates:
    #     logger.info(f"当前处理交易日：{trade_date}")
    #     # 每次调用 main() 生成一个 CSV 文件，并加入 temp_files 列表
    #     result = main(trade_date)
    #     temp_files.append(result)
    #
    # # 合并所有生成的 CSV 文件
    # df = merge_csv(temp_files, os.path.join(dc.filter_dir, f'tushare_stock_basic_filter4_merged.csv'))
    #
    # excel_path = os.path.join(dc.filter_dir, f'tushare_stock_basic_filter4_merged.xlsx')
    # save_to_excel(df, excel_path, sheet_name="Sheet1")

    # 获取最近交易日
    trade_date = get_last_trade_date()
    logger.info(f"当前处理交易日：{trade_date}")

    main(trade_date)
