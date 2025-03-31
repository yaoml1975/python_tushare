import os
import sys

from data_cache import dc
from stock_utils import setup_logger, get_last_trade_date, get_last_n_trade_dates, fetch_daily, fetch_daily_basic, \
    fetch_stock_basic, generate_quarter_list, fetch_fina_indicator_vip_by_quarter_str

logger = setup_logger()


def check_and_fetch(file_prefix, fetch_function, trade_dates):
    """检查 csv 是否存在，如果不存在则调用 fetch_function 生成"""
    for trade_date in trade_dates:
        filename = f"{file_prefix}_{trade_date}.csv"
        full_path = os.path.join(dc.csv_dir, filename)

        # 校验文件是否存在且文件内容有效
        if not os.path.exists(full_path) or not is_valid_csv(full_path):
            logger.info(f"{full_path} 不存在或无效，正在获取数据...")
            try:
                fetch_function(trade_date)
            except Exception as e:
                logger.error(f"获取数据失败: {e}")
        else:
            logger.info(f"{full_path} 已存在，跳过.")


def is_valid_csv(file_path):
    """检查 CSV 文件是否有效"""
    return os.path.getsize(file_path) > 0


def main():
    try:
        last_trade_date = get_last_trade_date()
        last_20_trade_dates = get_last_n_trade_dates(n=20)

        # 检查并获取股票基础信息（只执行一次）
        check_and_fetch("tushare_stock_basic", fetch_stock_basic, [last_trade_date])

        # 检查并获取最近 20 天的日线数据
        check_and_fetch("tushare_daily", fetch_daily, last_20_trade_dates)

        # 检查并获取最近 20 天的每日指标数据
        check_and_fetch("tushare_daily_basic", fetch_daily_basic, last_20_trade_dates)

        # 检查并获取自2023以来财报数据
        quarter_list = generate_quarter_list(2023)
        check_and_fetch("fetch_fina_indicator_vip", fetch_fina_indicator_vip_by_quarter_str, quarter_list)

    except KeyboardInterrupt:
        logger.error("检测到手动终止 (Ctrl + C)，程序已安全退出。")
        sys.exit(1)


if __name__ == "__main__":
    main()
