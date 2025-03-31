import tushare as ts
import yaml
import os
from data_cache import DataCache

class TushareWrapper:
    def __init__(self, config_path='config.yaml'):
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        self.pro = ts.pro_api(config['tushare']['token'])
        self.cache = DataCache(
            config['cache']['directory'],
            config['cache']['ttl_days']
        )
    
    def query(self, api_name, **kwargs):
        cache_key = f"{api_name}:{str(kwargs)}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached
            
        result = getattr(self.pro, api_name)(**kwargs)
        self.cache.set(cache_key, result)
        return result