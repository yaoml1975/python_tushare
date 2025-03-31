# filename: tushare_test1.py

import os
import sys
from datetime import datetime

import pandas as pd
from dateutil.relativedelta import relativedelta

from data_cache import dc
from stock_utils import fetch_stock_basic, setup_logger, load_csv, get_last_trade_date

logger = setup_logger()


def filter_recent_listings(df, years=2):
    """过滤近N年上市的股票"""
    current_date = datetime.now().date()
    cutoff_date = current_date - relativedelta(years=years)

    # 转换上市日期格式
    df['list_date'] = pd.to_datetime(
        df['list_date'],
        format='%Y%m%d',
        errors='coerce'
    ).dt.date

    # 过滤无效日期
    df = df.dropna(subset=['list_date'])

    # 应用日期过滤
    return df[df['list_date'] < cutoff_date]


def test1(last_trade_date):
    try:
        # 保存结果
        output_path = os.path.join(dc.filter_dir, f"tushare_stock_basic_filter1_{last_trade_date}.csv")
        if os.path.exists(output_path):
            logger.warning(f"最终筛选结果已存在，将无法写入：{output_path}")
            sys.exit(0)

        logger.info(f"当前处理交易日：{last_trade_date}")

        # 加载股票基础数据
        df = load_csv("tushare_stock_basic", fetch_stock_basic, last_trade_date)
        logger.info(f"初始数据量：{len(df)}条")

        # 过滤条件1：排除近两年上市
        # df = filter_recent_listings(df)
        # logger.info(f"排除新上市公司后：{len(df)}条")

        # 过滤条件2：排除ST股票
        df = df[~df['name'].str.contains('ST')]
        logger.info(f"排除ST股票后：{len(df)}条")

        # 过滤条件3：排除4/8/9开头股票[北交所股票的代码]
        df = df[~df['ts_code'].str[0].isin(['4', '8', '9'])]
        logger.info(f"排除4/8/9开头股票后：{len(df)}条")

        # 过滤条件4：仅保留市场类型为主板的股票
        # 主板涨跌幅约束为10%。创业板和科创板涨跌幅约束为20%。
        # df = df[df['market'] == '主板']
        # logger.info(f"仅保留主板股票后：{len(df)}条")

        # 过滤条件5：排除民营企业和外资企业
        # df = df[~df['act_ent_type'].isin(['民营企业', '外资企业'])]
        # logger.info(f"排除民营和外资企业后：{len(df)}条")

        # 过滤条件6：仅保留银行
        # df = df[df['industry'] == '银行']
        # logger.info(f"仅保留银行股票后：{len(df)}条")

        logger.info(f"最终筛选结果已保存至：{output_path}")
        df.to_csv(output_path, index=False, encoding='utf-8_sig')

        return df

    except Exception as e:
        logger.error(f"程序运行异常：{str(e)}", exc_info=True)
    except KeyboardInterrupt:
        logger.error("检测到手动终止 (Ctrl + C)，程序已安全退出。")
        sys.exit(1)


def main(last_trade_date):
    test1(last_trade_date)


if __name__ == "__main__":
    # 获取最近交易日
    trade_date = get_last_trade_date()
    logger.info(f"当前处理交易日：{trade_date}")

    main(trade_date)
