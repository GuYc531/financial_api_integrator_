import sys

import requests
import os
from datetime import datetime, timedelta
from logger import Logger
import logging
import pandas as pd
from dotenv import load_dotenv

load_dotenv()


class PolygonApiHandler:
    def __init__(self, ticker, date_to_fetch_from, date_to_fetch_till, number_of_time_frames, time_frame, adjusted,
                 sort, api_key, date_column_name, latest):
        """
        Initializes the PolygonApiHandler class with parameters necessary for
        fetching data from the Polygon API.

        This constructor sets up various parameters such as the stock ticker symbol, date range,
        the time frame for the data, and other configuration values. It also constructs the Polygon
        API URL based on whether you're fetching historical data or the latest data.

        Args:
            ticker (str): The stock ticker symbol to fetch data for.
            date_to_fetch_from (str): The start date for the data to fetch (format: YYYY-MM-DD).
            date_to_fetch_till (str): The end date for the data to fetch (format: YYYY-MM-DD).
            number_of_time_frames (str): The number of time frames to fetch in string.
            time_frame (str): The time frame for the data (e.g., "day", "minute").
            adjusted (bool): Whether to fetch adjusted data (True or False).
            sort (str): Sorting order for the data ("asc" for ascending or "desc" for descending).
            api_key (str): The API key for authenticating with the Polygon API.
            date_column_name (str): The name of the date column in the resulting DataFrame.
            latest (bool): If True, fetch the latest data for the ticker; if False, fetch historical data.

        Raises:
            ValueError: If the API key is not provided in the environment or as a parameter.

        Attributes:
            date_to_fetch_from (str): The start date for data fetching.
            date_to_fetch_till (str): The end date for data fetching.
            number_of_time_frames (str): Number of time frames to request from the API in string.
            time_frame (str): The requested time frame for the data.
            adjusted (str): Whether the data is adjusted in string for the URL
            sort (str): Sorting order for the data.
            ticker (str): The stock ticker symbol.
            latest (bool): Flag indicating if the latest data is requested.

        Example:
            # Example of initializing the class
            polygon_data = PolygonData(ticker="AAPL",
                                       date_to_fetch_from="2024-01-01",
                                       date_to_fetch_till="2024-12-31",
                                       number_of_time_frames='30',
                                       time_frame="day",
                                       adjusted=True,
                                       sort="asc",
                                       api_key="your_api_key",
                                       date_column_name="date",
                                       latest=False)
        """
        self.log = Logger(name=__name__, log_file="logs/app.log", level=logging.DEBUG).get_logger()
        self.date_column_name = date_column_name
        self.polygon_base_url = os.getenv('polygon_base_url')
        self.polygon_api_version = os.getenv('polygon_api_version')
        self.date_to_fetch_from = date_to_fetch_from
        self.date_to_fetch_till = date_to_fetch_till
        self.number_of_time_frames = number_of_time_frames
        self.time_frame = time_frame
        self.adjusted = adjusted
        self.sort = sort
        self.ticker = ticker
        self.latest = latest
        if not api_key:
            self.log.error("API key not found! Make sure it's set in your .env file")
            raise ValueError("API key not found! Make sure it's set in your .env file")
        self.polygon_url = f'{self.polygon_base_url}/{self.polygon_api_version}/aggs/ticker/{self.ticker}/range/{self.number_of_time_frames}/{time_frame}/{date_to_fetch_from}/{date_to_fetch_till}?adjusted={self.adjusted}&sort={self.sort}&apiKey={api_key}' \
            if not self.latest else f'{self.polygon_base_url}/{self.polygon_api_version}/aggs/ticker/{self.ticker}/range/1/{self.time_frame}/{datetime.now().date() - timedelta(days=1)}/{datetime.now().date()}?adjusted={self.adjusted}&sort={self.sort}&apiKey={api_key}'

    def get_polygon_data(self):
        """
        Fetches data from the Polygon API and adjusts the data for the specified ticker.

        This function sends an HTTP GET request to the Polygon API using the URL defined in
        the `self.polygon_url` attribute. It processes the returned JSON response, extracting
        relevant data (stock price or other financial data), converting Unix epoch timestamps
        into human-readable datetime objects, and adds the formatted date column to the DataFrame.

        The function logs the success of the request or any errors that occur during the process.

        Returns:
            pd.DataFrame: A DataFrame containing the processed data , else None.
        """
        polygon_response = requests.get(self.polygon_url)
        adjusted_data = None

        if polygon_response.status_code == 200:
            data = polygon_response.json()
            if 'results' in data.keys():
                data = data['results']
            else:
                self.log.error(f"one of the arguments to the API get request is invalid {self.polygon_url} \n")
                raise ValueError(f"one of the arguments to the API get request is invalid {self.polygon_url} \n"
                                 f"please read again the API doc in https://polygon.io/docs/stocks/get_v2_aggs_ticker__stocksticker__range__multiplier___timespan___from___to")

            adjusted_data = pd.DataFrame(data)
            adjusted_data['timestamp'] = adjusted_data['t'].apply(lambda epoch: datetime.fromtimestamp(epoch / 1000))
            adjusted_data[self.date_column_name] = adjusted_data['timestamp'].apply(lambda x: str(x.date()))
            adjusted_data['ticker'] = self.ticker
            self.log.info(f"successfully got data for ticker {self.ticker}:")
        else:
            self.log.error(f"Error {polygon_response.status_code}: {polygon_response.text}")
            sys.exit(0)

        return adjusted_data
