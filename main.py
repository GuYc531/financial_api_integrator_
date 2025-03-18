import logging
from logger import Logger

from frankfurter_api_handler import FrankfurterApiHandler
from polygon_api_handler import PolygonApiHandler
from currency_convertor import convert_currency_in_stock_price_df
from config_handler import Configs

from dotenv import load_dotenv

load_dotenv()

log = Logger(name=__name__, log_file="logs/app.log", level=logging.DEBUG).get_logger()

configs = Configs()

frankfurter_handler = FrankfurterApiHandler(base_currency=configs.base_currency,
                                            date_to_fetch_from=configs.date_to_fetch_from,
                                            date_to_fetch_till=configs.date_to_fetch_till,
                                            ticker=configs.ticker,
                                            date_column_name=configs.date_column_name,
                                            latest=configs.latest)

currency_data = frankfurter_handler.get_frankfurter_data()

polygon_api_handler = PolygonApiHandler(date_to_fetch_from=configs.date_to_fetch_from,
                                        date_to_fetch_till=configs.date_to_fetch_till,
                                        ticker=configs.ticker,
                                        time_frame=configs.time_frame,
                                        adjusted=configs.adjusted,
                                        number_of_time_frames=configs.number_of_time_frames,
                                        date_column_name=configs.date_column_name,
                                        sort=configs.sort, api_key=configs.api_key, latest=configs.latest)

stock_price_data = polygon_api_handler.get_polygon_data()

convertion_is_valid = True

if configs.currency_to_convert_to not in currency_data.columns:
    convertion_is_valid = False
    log.debug(f"currency to convert {configs.currency_to_convert_to} is invalid leaving the currency as {configs.base_currency}")

for col in configs.stock_price_column_to_convert:
    if col not in stock_price_data.columns:
        log.debug(
            f"column {col}, being removed from stock_price_column_to_convert because it is not in stock_price_data "
            f"columns to convert based on selected currency please select one of"
            f"{str(stock_price_data.columns)}")
        configs.stock_price_column_to_convert.remove(col)


if stock_price_data is not None and currency_data is None:
    convertion_is_valid = False
    log.debug(f"only have stock price data and not currency data so will save currency base on USD")

if convertion_is_valid:
    stock_price_data, timestamp = convert_currency_in_stock_price_df(stock_price_data=stock_price_data,
                                                            latest=configs.latest,
                                                            currency_data=currency_data,
                                                            currency_to_convert_to=configs.currency_to_convert_to,
                                                            date_column_name=configs.date_column_name,
                                                            stock_price_column_to_convert=configs.stock_price_column_to_convert)
    currency_data['timestamp'] = timestamp
    currency_data.drop('Date', axis=1, inplace=True)
else:
    stock_price_data['currency'] = configs.base_currency

log.info(f"successfully created object stock_price_data ready to insert to DB")

# insert to database table based on 'time_frame' value table

# final_stock_price_data(['v', 'vw', 'o', 'c', 'h', 'l', 't', 'n', 'timestamp', 'ticker'], dtype='object')

# currency_data(['AUD', 'BGN', 'BRL', 'CAD', 'CHF', 'CNY', 'CZK', 'DKK', 'EUR', 'GBP',
#        'HKD', 'HUF', 'IDR', 'ILS', 'INR', 'ISK', 'JPY', 'KRW', 'MXN', 'MYR',
#        'NOK', 'NZD', 'PHP', 'PLN', 'RON', 'SEK', 'SGD', 'THB', 'TRY', 'ZAR',
#        'base_currency', 'timestamp'],
#       dtype='object')
