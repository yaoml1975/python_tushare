# filename: tushare_test2.py
import os
import sys

import pandas as pd

from data_cache import dc
from stock_utils import setup_logger, get_last_trade_date, fetch_daily_basic, load_csv
from tushare_test1 import test1

logger = setup_logger()


def test2(last_trade_date):
    try:
        # 保存结果
        output_path = os.path.join(dc.filter_dir, f"tushare_stock_basic_filter2_{last_trade_date}.csv")
        if os.path.exists(output_path):
            logger.error(f"筛选结果 CSV 文件已存在，将无法写入: {output_path}")
            sys.exit(0)

        # 加载基础筛选结果（csv1）
        df_basic = load_csv("tushare_stock_basic_filter1", test1, last_trade_date)
        logger.info(f"基础筛选结果（csv1）股票数量：{len(df_basic)}")

        # 加载日线行情数据（csv2）
        # df_daily = load_csv("tushare_daily", fetch_daily, last_trade_date)
        # logger.info(f"日线行情数据（csv2）股票数量：{len(df_daily)}")

        # 加载每日指标数据（csv3）
        df_daily_basic = load_csv("tushare_daily_basic", fetch_daily_basic, last_trade_date)
        logger.info(f"每日指标数据（csv3）股票数量：{len(df_daily_basic)}")

        # 检查 csv2 和 csv3 是否包含 csv1 的所有股票
        # missing_in_csv2 = set(df_basic["ts_code"]) - set(df_daily["ts_code"])
        # if missing_in_csv2:
        #     logger.warning(f"csv2 中缺少以下股票 [今天可能停牌] ：{missing_in_csv2}")

        missing_in_csv3 = set(df_basic["ts_code"]) - set(df_daily_basic["ts_code"])
        if missing_in_csv3:
            logger.warning(f"csv3 中缺少以下股票 [可能今天停牌] ：{missing_in_csv3}")

        # 仅合并 csv1 中包含的股票
        # 如果 csv2 或 csv3 中没有 csv1 中某些股票的数据，pd.merge 的 how="inner" 会将这些股票从结果中排除。
        # 没有的原因可能是停牌
        # df_merged = pd.merge(df_basic, df_daily, on="ts_code", how="left")
        # df_merged = pd.merge(df_merged, df_daily_basic, on="ts_code", how="left")
        # logger.info(f"合并后（csv1 + csv2 + csv3）股票数量：{len(df_merged)}")

        df_merged = pd.merge(df_basic, df_daily_basic, on="ts_code", how="left")
        logger.info(f"合并后（csv1 + csv3）股票数量：{len(df_merged)}")

        # 筛选条件：流通市值（单位：万元） <= 10,000,000万元（即1000亿元）
        df_filtered = df_merged[
            (df_merged["circ_mv"] <= dc.circ_mv)  # 流通市值（单位：万元） <= 1000 亿
            # & (df_merged["pe"].between(5, 50))  # 市盈率在 5 到 50 之间
        ]
        logger.info(f"筛选后股票数量：{len(df_filtered)}")

        df_filtered.to_csv(output_path, index=False, encoding="utf-8_sig")
        logger.info(f"筛选结果已保存至：{output_path}")

    except Exception as e:
        logger.error(f"程序运行异常：{str(e)}", exc_info=True)
    except KeyboardInterrupt:
        logger.error("检测到手动终止 (Ctrl + C)，程序已安全退出。")
        sys.exit(1)


def main(last_trade_date):
    test2(last_trade_date)


if __name__ == "__main__":
    # 获取最近交易日
    trade_date = get_last_trade_date()
    logger.info(f"当前处理交易日：{trade_date}")

    main(trade_date)
