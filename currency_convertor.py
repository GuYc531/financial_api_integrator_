from typing import List, Tuple, Any

import pandas as pd


def convert_currency_in_stock_price_df(stock_price_data: pd.DataFrame, latest: int, currency_data: pd.DataFrame,
                                       date_column_name: str,
                                       stock_price_column_to_convert: List[str],
                                       currency_to_convert_to: str) -> Tuple[pd.DataFrame, Any]:
    """
        Converts stock prices in a DataFrame from one currency to another based on the provided currency data.

        This function adjusts the stock prices in the `stock_price_data` DataFrame by multiplying them with
        the corresponding exchange rates from the `currency_data` DataFrame. It handles both the latest data
        scenario and historical data by merging the data on the provided date column. The function also
        interpolates missing currency values for historical data.

        Args:
            stock_price_data (pd.DataFrame): DataFrame containing stock prices to be converted.
            latest (int): Flag to indicate if only the latest data is being used (1 for latest, 0 for historical).
            currency_data (pd.DataFrame): DataFrame containing the currency exchange rates, including the target currency.
            date_column_name (str): The name of the date column in both stock price and currency data.
            stock_price_column_to_convert (List[str]): List of column names in `stock_price_data` containing the stock prices to be converted.
            currency_to_convert_to (str): The target currency to convert the stock prices into.

        Returns:
            pd.DataFrame: The adjusted stock price DataFrame with converted prices in the specified target currency.
            timestamp: of the latest observation from the stock_price_data 'timestamp' column
        Example:
            # Example of converting stock prices using the latest currency exchange data
            adjusted_stock_prices = convert_currency_in_stock_price_df(stock_price_data=stock_df,
                                                                        latest=True,
                                                                        currency_data=currency_df,
                                                                        date_column_name="Date",
                                                                        stock_price_column_to_convert=["close"],
                                                                        currency_to_convert_to="EUR")
        """
    if stock_price_data is not None and currency_data is not None:
        if latest:
            stock_price_data = stock_price_data.merge(currency_data[[date_column_name, currency_to_convert_to]],
                                                      how='cross')
            stock_price_data[stock_price_column_to_convert] = stock_price_data[stock_price_column_to_convert].apply(
                lambda x: x * stock_price_data[currency_to_convert_to])
            stock_price_data.drop(
                columns=[date_column_name + '_x', date_column_name + '_y', currency_to_convert_to],
                inplace=True, axis=1)

        else:
            stock_price_data = stock_price_data.merge(currency_data[[date_column_name, currency_to_convert_to]],
                                                      on=date_column_name, how='left')
            if stock_price_data[currency_to_convert_to].isna().sum() > 0:
                stock_price_data[currency_to_convert_to].interpolate()

            stock_price_data[stock_price_column_to_convert] = stock_price_data[stock_price_column_to_convert].apply(
                lambda x: x * stock_price_data[currency_to_convert_to])
            stock_price_data.drop(currency_to_convert_to, inplace=True, axis=1)
            stock_price_data.drop(date_column_name, inplace=True, axis=1)

    stock_price_data['currency'] = currency_to_convert_to
    return stock_price_data, max(stock_price_data['timestamp'])
