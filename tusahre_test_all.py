# filename: tushare_test_all.py

import tushare_test1
import tushare_test2
import tushare_test3
import tushare_test4
from stock_utils import setup_logger, get_friday_trade_dates

logger = setup_logger()


def main():
    friday_trade_dates = get_friday_trade_dates(2025, 2)

    for trade_date in friday_trade_dates:
        logger.info(f'运行日期: {trade_date}')

        logger.info('-' * 20 + ' tushare_test1.main() ' + '-' * 20)
        tushare_test1.main(trade_date)

        logger.info('-' * 20 + ' tushare_test2.main() ' + '-' * 20)
        tushare_test2.main(trade_date)

        logger.info('-' * 20 + ' tushare_test3.main() ' + '-' * 20)
        tushare_test3.main(trade_date)

        logger.info('-' * 20 + ' tushare_test4.main() ' + '-' * 20)
        tushare_test4.main(trade_date)

        logger.info(f'*' * 100)


if __name__ == '__main__':
    main()
