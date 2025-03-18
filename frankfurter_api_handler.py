import requests
import os
from datetime import datetime
from logger import Logger
import logging
import pandas as pd
from dotenv import load_dotenv

load_dotenv()


class FrankfurterApiHandler:
    def __init__(self, ticker, date_to_fetch_from, date_to_fetch_till,
                 base_currency, date_column_name, latest):
        """
            Initializes the FrankfurterApiHandler class with parameters necessary for
            fetching exchange rate data from the Frankfurter API.

            This constructor sets up the parameters such as stock ticker, date range, base currency, and
            other configuration values. It constructs the URL for the Frankfurter API based on whether you're
            fetching historical data or the latest data.

            Args:
                ticker (str): The ticker symbol associated with the data.
                date_to_fetch_from (str): The start date for the data to fetch (format: YYYY-MM-DD).
                date_to_fetch_till (str): The end date for the data to fetch (format: YYYY-MM-DD).
                base_currency (str): The base currency for the exchange rate data (e.g., "USD").
                date_column_name (str): The name of the date column in the resulting DataFrame.
                latest (bool): If True, fetch the latest exchange rates for the base currency; if False, fetch historical rates.

            Attributes:
                date_to_fetch_from (str): The start date for data fetching.
                date_to_fetch_till (str): The end date for data fetching.
                base_currency (str): The base currency for the exchange rate data.
                latest (bool): Flag indicating if the latest data is requested.
                ticker (str): The stock ticker symbol.
                date_column_name (str): The name of the date column in the resulting DataFrame.

            Example:
                # Example of initializing the class
                frankfurter_data = FrankfurterData(ticker="USD",
                                                   date_to_fetch_from="2024-01-01",
                                                   date_to_fetch_till="2024-12-31",
                                                   base_currency="USD",
                                                   date_column_name="date",
                                                   latest=False)
            """
        self.date_column_name = date_column_name
        self.frankfurter_base_url = os.getenv('frankfurter_base_url')
        self.frankfurter_api_version = os.getenv('frankfurter_api_version')
        self.date_to_fetch_from = date_to_fetch_from
        self.date_to_fetch_till = date_to_fetch_till
        self.base_currency = base_currency
        self.latest = latest
        self.frankfurter_url = f"{self.frankfurter_base_url}/{self.frankfurter_api_version}/{self.date_to_fetch_from}..{self.date_to_fetch_till}?base={self.base_currency}" \
            if not latest else f"{self.frankfurter_base_url}/{self.frankfurter_api_version}/latest?base={self.base_currency}"
        self.ticker = ticker
        self.log = Logger(name=__name__, log_file="logs/app.log", level=logging.DEBUG).get_logger()

    def get_frankfurter_data(self):
        """
            Fetches exchange rate data from the Frankfurter API and adjusts it into a DataFrame.

            This function sends an HTTP GET request to the Frankfurter API using the URL defined in
            the `self.frankfurter_url` attribute. It processes the returned JSON response, extracting
            the exchange rate data, and then formats it into a DataFrame with a date column. The function
            handles both cases when the API returns a flat dictionary of rates or a nested structure.

            The function logs the success of the request or any errors that occur during the process.

            Returns:
                pd.DataFrame: A DataFrame containing the exchange rate data,for all currencies available
                              with the rates as columns and the date as the index, if the request was successful;
                               else, None.

            """
        frankfurter_response = requests.get(self.frankfurter_url)
        adjusted_data = None

        if frankfurter_response.status_code == 200:
            data = frankfurter_response.json()
            if 'rates' in data.keys():

                data = data['rates']
            else:
                self.log.error(f"one of the variables in the URL is wrong {self.frankfurter_url}")
            if isinstance(list(data.values())[0], float):
                adjusted_data = pd.DataFrame({str(datetime.now().date()): data}).transpose()

            else:
                adjusted_data = pd.DataFrame(data).transpose()

            adjusted_data[self.date_column_name] = adjusted_data.index
            adjusted_data['base_currency'] = self.base_currency
            self.log.info(f"successfully got data for ticker {self.ticker}:")
        else:
            self.log.error(f"Error {frankfurter_response.status_code}: {frankfurter_response.text}")

        return adjusted_data
