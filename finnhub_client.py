from abc import ABC
from typing import List, Union
import numpy as np

from date import Date
from base import BaseClient
from requests import Session

from models.finnhub import *


class FinnhubClient(BaseClient, ABC):
    base_url = "https://finnhub.io/api/v1"

    def __init__(self, api_key: str = None, proxy: str = None):
        self._api_key = api_key
        self._proxy = proxy

    @property
    def api_key(self):
        return self._api_key

    @property
    def proxy(self):
        return self._proxy if self._proxy is None else {self._proxy}

    @property
    def session(self):
        return Session()

    def _get_url(self, route: str) -> str:
        return self.base_url + route

    @property
    def headers(self) -> dict:
        return {"X-Finnhub-Token": self.api_key, "Accepts": "application/json"}

    @staticmethod
    def _merge_two_dicts(first: dict, second: dict) -> dict:
        result = first.copy()
        result.update(second)
        return result

    def get_quote(self, symbol: str) -> pd.DataFrame:
        params = {"symbol": symbol}
        response = self._get("/quote", params=params)
        return Quote.get(**response)

    def get_stock_candles(self, symbol: str, resolution: str, _from: datetime, to: datetime) -> pd.DataFrame:
        _from, to = Date.datetime_to_timestamp(_from, to)
        params = {
            "symbol": symbol,
            "resolution": resolution,
            "from": _from,
            "to": to
        }
        response = self._get("/stock/candle", params=params)
        return Candles.get(**response)

    def get_stock_close(self, symbol: str, resolution: str, _from: datetime, to: datetime) -> pd.Series:
        df_candles = self.get_stock_candles(symbol, resolution, _from, to)
        return df_candles['close']

    def get_technical_indicator(self, symbol: str, resolution: str, _from: datetime, to: datetime, indicator: str,
                                indicator_fields: dict) \
            -> Union[pd.DataFrame, pd.Series]:
        params = self._merge_two_dicts({
            "symbol": symbol,
            "resolution": resolution,
            "from": _from,
            "to": to,
            "indicator": indicator
        }, indicator_fields)
        response = self._get("/indicator", params=params)
        return TechnicalIndic(**response).get(indicator_fields.get('timeperiod'))

    def get_multiple_technical_indicator(self, symbol: str, resolution: str, _from: datetime, to: datetime,
                                         indicators: list = ['sma', 'sma', 'bbands'],
                                         time_indicators: list = [20, 60, 20]) -> pd.DataFrame:
        list_df_indic = []
        for indic, time in zip(indicators, time_indicators):
            start_ti_shift = _from - timedelta(days=Date.from_business(int(time)))
            start_ti, end_ti = Date.datetime_to_timestamp(start_ti_shift, to)
            df_tech_indic = self.get_technical_indicator(symbol, resolution, start_ti,
                                                         end_ti, indic,
                                                         {"timeperiod": time})
            close = df_tech_indic.pop('c')
            list_df_indic.append(df_tech_indic)
        list_df_indic.append(close.to_frame('close'))
        df_multiple_indic = pd.concat(list_df_indic, join='inner', axis=1)
        df_multiple_indic = df_multiple_indic.iloc[np.max(np.where(df_multiple_indic == 0)[0]) + 1:]
        if -1 < df_multiple_indic.mean().min() < 1: df_multiple_indic.drop('close', axis=1, inplace=True)
        return df_multiple_indic

    def get_company_news(self, symbol: str, time=5, nb=10) -> pd.DataFrame:
        _from, to = Date.datetime_to_str(datetime.today() - timedelta(days=5), datetime.today())
        params = {
            "symbol": symbol,
            "from": _from,
            "to": to
        }
        response = self._get("/company-news", params=params)
        return pd.concat(list(map(lambda item: News.get(time, **item), response[0:nb])))

    def get_company_peers(self, symbol: str) -> list:
        params = {"symbol": symbol}
        return self._get("/stock/peers", params=params)

    def get_company_basic_financials(self, symbol: str, metric: str = 'all') -> pd.DataFrame:
        params = {
            "symbol": symbol,
            "metric": metric
        }
        response = self._get("/stock/metric", params=params)
        return Financials.get(**response)

    def get_peers_basic_financials(self, symbol: str, metric: str = 'all') -> pd.DataFrame:
        data = self.get_company_basic_financials(symbol, metric)
        symbol = data.index
        peers = self.get_company_peers(symbol)
        peers.remove(symbol)
        if len(peers) > 2:
            list_df_peers = [data]
            for peer in peers:
                list_df_peers.append(self.get_company_basic_financials(peer, metric))
            return pd.concat(list_df_peers)
        else:
            return data

    def get_stock_insider_transactions(self, symbol: str, _from=None, to=None, nb=10) -> pd.DataFrame:
        params = {
            "symbol": symbol,
            "from": _from,
            "to": to
        }
        response = self._get("/stock/insider-transactions", params=params)
        return pd.concat(list(map(lambda item: Insiders.get(**item), response.get('data')))).iloc[0:nb]

    def get_recommendation_trends(self, symbol: str) -> pd.DataFrame:
        params = {"symbol": symbol}
        response = self._get("/stock/recommendation", params=params)
        return pd.concat(list(map(lambda item: Reco.get(**item), response)))

    def get_company_earnings(self, symbol: str, limit=None) -> pd.DataFrame:
        params = {
            "symbol": symbol,
            "limit": limit
        }
        response = self._get("/stock/earnings", params=params)
        return pd.concat(list(map(lambda item: Earns.get(**item), response)))

    def get_stock_social_sentiment(self, symbol: str, _from=None, to=None, nb=10) -> pd.DataFrame:
        _from, to = Date.datetime_to_str(_from, to)
        params = {
            "symbol": symbol,
            "from": _from,
            "to": to
        }
        response = self._get("/stock/social-sentiment", params=params)
        df_reddit = pd.concat(
            list(map(lambda item: Sentiment.get(**item), response.get('reddit')))[0:nb])
        df_twitter = pd.concat(
            list(map(lambda item: Sentiment.get(**item), response.get('twitter')))[0:nb])
        return df_reddit, df_twitter


if __name__ == '__main__':

    """
    To Debug before using streamlit
    """

    finnhub_client = FinnhubClient("c87vgoaad3iet0qj4jcg")

    symbol = 'AAPL'
    start = datetime(2020, 3, 12)
    end = datetime(2022, 3, 11)
    delta_time = 'D'

    df_quote = finnhub_client.get_quote(symbol)
    df_candles = finnhub_client.get_stock_candles(symbol, delta_time, start, end)

    df_multiple_indic = finnhub_client.get_multiple_technical_indicator(symbol, delta_time, start, end)

    df_company_news = finnhub_client.get_company_news(symbol)
    df_financials = finnhub_client.get_peers_basic_financials(symbol)
    df_insiders = finnhub_client.get_stock_insider_transactions(symbol)
    df_recommendation = finnhub_client.get_recommendation_trends(symbol)
    df_earnings = finnhub_client.get_company_earnings(symbol)
    df_sentiment_reddit, df_sentiment_twitter = finnhub_client.get_stock_social_sentiment(symbol, start, end)

    print('end')
