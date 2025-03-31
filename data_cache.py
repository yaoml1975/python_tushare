# filename: data_cache.py

import os
import threading

import pandas as pd
import tushare as ts
import yaml


class Singleton(object):
    _instance_lock = threading.Lock()
    _config = None  # 添加一个类属性来存储配置信息

    def __init__(self):
        if self._config is None:
            self._load_config()

    def _load_config(self):
        # 获取当前脚本所在的目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # 构建 config.yaml 的绝对路径
        config_path = os.path.join(current_dir, 'config.yaml')
        print("Loading config from:", config_path)
        with open(config_path, 'r', encoding="utf-8") as f:
            self._config = yaml.safe_load(f)

        # 设置实例属性
        self.csv_dir = self._config['paths']['csv_dir']
        self.log_dir = self._config['paths']['log_dir']
        self.filter_dir = self._config['paths']['filter_dir']
        self.token = self._config["tushare"]["token"]

        self.circ_mv = self._config['stock_selection']['circ_mv']  # 流通市值，单位：万元
        self.roe = self._config['stock_selection']['roe']  # 净资产收益率（ROE）不低于 >= 4%
        self.q_netprofit_yoy = self._config["stock_selection"]["q_netprofit_yoy"]  # 净利润增长率（同比）大于 > 0%
        self.debt_to_assets = self._config["stock_selection"]["debt_to_assets"]  # 资产负债率 < 80%
        self.top_volume = self._config["stock_selection"]["top_volume"]  # 成交额降序排列的前n名
        self.top_pct_chg = self._config["stock_selection"]["top_pct_chg"]  # 涨幅降序排列的前n名

        self.period_year = self._config["period_or_end_date"]["year"]  # 用于生成报告期(每个季度最后一天的日期
        self.period_quarter = self._config["period_or_end_date"]["quarter"]  # 用于生成报告期(每个季度最后一天的日期

        # 确保目录存在
        os.makedirs(self.csv_dir, exist_ok=True)
        os.makedirs(self.log_dir, exist_ok=True)
        os.makedirs(self.filter_dir, exist_ok=True)

        # 初始化 Tushare API
        self.pro = ts.pro_api(self.token)

        # 构建 中文 -> 英文 字段映射
        self.zh_to_en = {}
        for api_name, api_info in self._config["apis"].items():
            for en_name, zh_name in api_info["fields"].items():
                self.zh_to_en[zh_name] = {"api_name": api_name, "field_name": en_name}

    def __new__(cls, *args, **kwargs):
        if not hasattr(Singleton, "_instance"):
            with Singleton._instance_lock:
                if not hasattr(Singleton, "_instance"):
                    Singleton._instance = object.__new__(cls)

        return Singleton._instance

    # 中文字段到API名称的映射find_one
    def find_api_and_field(self, chinese_field):
        for api_name, api_info in self._config['apis'].items():
            for field, field_name in api_info['fields'].items():
                if field_name == chinese_field:
                    return api_name, field
        return None, None

    # 中文字段到API名称的映射find_all
    def find_all_api_and_fields(self, chinese_field):
        results = []
        for api_name, api_info in self._config['apis'].items():
            for field, field_name in api_info['fields'].items():
                if field_name == chinese_field:
                    results.append((api_name, field))
        return results

    # 中文字段到API名称的模糊查找
    def fuzzy_find_api_and_fields(self, chinese_field):
        results = []
        for api_name, api_info in self._config['apis'].items():
            for field, field_name in api_info['fields'].items():
                if chinese_field in field_name:  # 模糊匹配
                    results.append((api_name, field, field_name))
        return results

    def fetch_data(self, api_name, params):
        """ 调用 Tushare API 获取数据 """
        if api_name not in self._config["apis"]:
            raise ValueError(f"未找到 {api_name} 对应的 API 配置")

        api_info = self._config["apis"][api_name]
        tushare_api = api_info["tushare_api"]
        fields = list(api_info["fields"].keys())

        df = self.pro.query(tushare_api, **params, fields=",".join(fields))
        return df

    def get_data(self, zh_name, date, params=None):
        """ 通过中文指标名获取数据（优先本地缓存，否则调用 API） """
        if params is None:
            params = {}  # 如果没有传入params，初始化为空字典
        api_name, field_name = self.find_api_and_field(zh_name)
        if not field_name:
            raise ValueError(f"找不到指标: {zh_name}")

        api_info = self._config["apis"][api_name]
        date_field = api_info["date_field"]

        params[date_field] = date  # 设置日期参数

        file_path = os.path.join(self.csv_dir, f"tushare_{api_name}_{date}.csv")

        # 1. 读取本地缓存
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            print(f"读取本地数据: {file_path}")
        else:
            # 2. 本地无数据，调用 Tushare API
            print(f"调用 Tushare API: {api_name}")
            df = self.fetch_data(api_name, params)
            if not df.empty:
                df.to_csv(file_path, index=False, encoding='utf-8_sig')
                print(f"数据已存入: {file_path}")

        return df[[field_name]] if field_name in df.columns else df


dc = Singleton()
