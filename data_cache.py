import os
import pickle
from datetime import datetime, timedelta
import hashlib

class DataCache:
    def __init__(self, cache_dir='./data_cache', ttl_days=7):
        self.cache_dir = cache_dir
        self.ttl_days = ttl_days
        os.makedirs(cache_dir, exist_ok=True)
    
    def _get_cache_path(self, key):
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{key_hash}.pkl")
    
    def get(self, key):
        cache_path = self._get_cache_path(key)
        if not os.path.exists(cache_path):
            return None
            
        with open(cache_path, 'rb') as f:
            data, timestamp = pickle.load(f)
            
        if datetime.now() - timestamp > timedelta(days=self.ttl_days):
            os.remove(cache_path)
            return None
            
        return data
    
    def set(self, key, data):
        cache_path = self._get_cache_path(key)
        with open(cache_path, 'wb') as f:
            pickle.dump((data, datetime.now()), f)