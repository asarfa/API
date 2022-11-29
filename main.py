import streamlit as st
import numpy as np
import pandas as pd
from finnhub_client import FinnhubClient
from date import Date
from go_plotly import Graph
from datetime import datetime, date, timedelta


class StreamFin:
    def __init__(self, api_key: str = None, proxy: str = None):
        self._api_key = api_key
        self._proxy = proxy

    @staticmethod
    def instanciate_days():
        yesterday = date.today()
        yesterday = Date.nearest_business_day_end(yesterday)
        default_start = yesterday - timedelta(days=365)
        default_start = Date.nearest_business_day_start(default_start)
        col1, col2 = st.columns(2)
        start = col1.date_input("From", value=default_start, max_value=yesterday)
        end = col2.date_input("To", value=yesterday, max_value=yesterday, min_value=start)
        start = datetime.fromordinal(Date.nearest_business_day_start(start).toordinal())
        end = datetime.fromordinal(Date.nearest_business_day_end(end).toordinal())
        return start, end

    @staticmethod
    def instanciate_stocks_freq():
        col1, col2 = st.columns(2)
        stocks = np.array(["AAPL", "GOOG", "FB", 'TSLA'])
        symbol = col1.selectbox("Select stock", stocks)
        freq = np.array(["D", "W", "M", "1", "5", "15", "30", "60"])
        delta_time = col2.selectbox("Select frequency", freq)
        return symbol, delta_time

    @staticmethod
    def compute_quote(client: FinnhubClient, symbol: str):
        st.markdown("Real-time quote data")
        df_quote = client.get_quote(symbol)
        st.dataframe(df_quote)

    @staticmethod
    def compute_close(client: FinnhubClient, symbol: str, resolution: str, start: datetime, end: datetime):
        st.markdown("Graph asset's close")
        serie_close = client.get_stock_close(symbol, resolution, start, end)
        Graph.plot_line_data(serie_close)
        return serie_close

    @staticmethod
    def compute_ret(serie: pd.Series):
        ret = serie.pct_change()
        ret_add = ret.add(1)
        cumul_annual_ret = pd.Series(np.array(ret_add.cumprod()) **
                                     (np.arange(0, len(serie), 1) / 252) - 1, index=serie.index).iloc[1:]
        return ret, cumul_annual_ret

    def compute_stats(self, serie: pd.Series):
        ret, cumul_annual_ret = self.compute_ret(serie)
        st.markdown("Graph asset's return")
        Graph.plot_hist_data(ret)
        st.markdown("Descriptive stats on asset's returns")
        st.write(pd.DataFrame(ret.describe()).T)
        st.markdown("Graph cumulative annualised asset's returns")
        Graph.plot_line_data(cumul_annual_ret)
        st.markdown("Descriptive stats on cumulative annualised asset's returns")
        st.write(pd.DataFrame(cumul_annual_ret.describe()).T)

    @staticmethod
    def compute_technicals_indic(client: FinnhubClient, symbol: str, resolution: str, start: datetime, end: datetime):
        st.markdown("Technical indicator")
        indicators = st.multiselect(
            'What technical indicators needed',
            ['sma', 'ema', 'wma', 'tema', 'trima', 'kama', 'mama', 'rsi', 'willr', 'adx', 'adxr', 'apo', 'roc', 'rocr',
             'bbands', 'midpoint', 'midprice', 'atr'] * 3)
        time_indicators = []
        if len(indicators) > 0:
            seed = 0
            for indicator in indicators:
                time_indicators.append(st.text_input(
                    f'What time period needed for {indicator} indicators', key=seed))
                seed += 1
            condition = True
        else:
            condition = False
        if st.button("Get Technical Analysis"):
            df_multiple_indic = client.get_multiple_technical_indicator(symbol, resolution, start, end,
                                                                                indicators, time_indicators) if \
                condition else client.get_multiple_technical_indicator(symbol, resolution, start, end)
            Graph.plot_line_data(df_multiple_indic)

    @staticmethod
    def compute_company_news(client: FinnhubClient, symbol: str):
        st.markdown("List latest company news")
        df_company_news = client.get_company_news(symbol)
        st.dataframe(df_company_news)

    @staticmethod
    def compute_company_financials(client: FinnhubClient, symbol: str):
        st.markdown("Get company basic financials and compare with peers")
        df_financials = client.get_peers_basic_financials(symbol)
        st.dataframe(df_financials)

    @staticmethod
    def compute_company_insiders(client: FinnhubClient, symbol: str):
        st.markdown("Company insider transactions data sourced")
        df_insiders = client.get_stock_insider_transactions(symbol)
        st.dataframe(df_insiders)

    @staticmethod
    def compute_company_recommendation(client: FinnhubClient, symbol: str):
        st.markdown("Get latest analyst earnings")
        df_recommendation = client.get_recommendation_trends(symbol)
        st.dataframe(df_recommendation)

    @staticmethod
    def compute_company_earnings(client: FinnhubClient, symbol: str):
        st.markdown("Company insider transactions data sourced")
        df_earnings = client.get_company_earnings(symbol)
        st.dataframe(df_earnings)

    @staticmethod
    def compute_company_sentiment(client: FinnhubClient, symbol: str, start: datetime, end: datetime):
        st.markdown("Get social sentiment for stocks on Reddit and Twitter")
        df_sentiment_reddit, df_sentiment_twitter = client.get_stock_social_sentiment(symbol, start, end)
        col1, col2 = st.columns(2)
        col1.dataframe(df_sentiment_reddit)
        col2.dataframe(df_sentiment_twitter)

    def main(self):
        finnhub_client = FinnhubClient(self._api_key, self._proxy)
        st.title(""" Stock Analysis """)
        start, end = self.instanciate_days()
        symbol, delta_time = self.instanciate_stocks_freq()
        if st.button("Get Quantitative Data"):
            self.compute_quote(finnhub_client, symbol)
            serie_close = self.compute_close(finnhub_client, symbol, delta_time, start, end)
            self.compute_stats(serie_close)
        self.compute_technicals_indic(finnhub_client, symbol, delta_time, start, end)
        if st.button("Get Fundamental Data"):
            self.compute_company_news(finnhub_client, symbol)
            self.compute_company_financials(finnhub_client, symbol)
            self.compute_company_insiders(finnhub_client, symbol)
            self.compute_company_recommendation(finnhub_client, symbol)
            self.compute_company_earnings(finnhub_client, symbol)
            self.compute_company_sentiment(finnhub_client, symbol, start, end)


if __name__ == '__main__':

    #To open the streamlit app on a browser: Command line: streamlit run path_user/API_project/main.py

    key = "c87vgoaad3iet0qj4jcg"
    StreamFin(key).main()

