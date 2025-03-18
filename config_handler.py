import os
from types import NoneType

from logger import Logger
import logging

class Configs:
    def __init__(self):
        self.log = Logger(name=__name__, log_file="logs/app.log", level=logging.DEBUG).get_logger()
        self.api_key = os.getenv('POLYGON_API_KEY')
        self.latest = False if int(os.getenv('latest')) == 0 else True

        self.date_column_name = os.getenv('date_column_name')
        self.ticker = os.getenv('ticker')
        self.date_to_fetch_from = os.getenv('date_to_fetch_from')
        self.date_to_fetch_till = os.getenv('date_to_fetch_till')
        self.sort = os.getenv('sort')
        self.time_frame = os.getenv('time_frame')
        self.number_of_time_frames = os.getenv('number_of_time_frames')
        self.adjusted = os.getenv('adjusted')
        self.polygon_api_version = os.getenv('polygon_api_version')
        self.base_currency = os.getenv('base_currency')
        self.currency_to_convert_to = os.getenv('currency_to_convert_to')
        self.stock_price_column_to_convert = [i for i in list(os.getenv('stock_price_column_to_convert')) if i != ',']
        self._validate_environment_variables()
        self.log.info("all env vars initialized correctly")

    def _validate_environment_variables(self):
        for (env_var_key, env_var_val) in self.__dict__.items():
            if isinstance(env_var_val, NoneType):
                self.log.error(f"Notice, user did not initialize environment variable {env_var_key}")