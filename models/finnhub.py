import pandas as pd
from datetime import datetime, timedelta
from dataclasses import dataclass


class Data:

    @classmethod
    def from_json(cls, **kwargs):
        return cls(**{key: kwargs.get(key) for key in cls.__dict__.keys() & kwargs.keys()})

    @classmethod
    def dict_from_json(cls, **kwargs):
        return cls.from_json(**kwargs).__dict__

    @classmethod
    def from_json_outer(cls, **kwargs):
        return cls(**{key: kwargs.get(key) for key in kwargs.keys() - Trash.__dict__.keys()})


@dataclass
class Quote(Data):
    c: float = None
    dp: float = None
    h: float = None
    l: float = None

    @staticmethod
    def get(**kwargs) -> pd.DataFrame:
        obj = Quote.from_json(**kwargs)
        df = pd.DataFrame([obj.__dict__.values()], columns=["spot", "changePercent", "high", "low"],
                          index=["latest_quote"])
        return df


@dataclass
class Candles(Data):
    c: float = None
    h: float = None
    l: float = None
    o: float = None
    t: datetime.timestamp = None
    v: float = None

    @staticmethod
    def get(**kwargs) -> pd.DataFrame:
        obj_dict = Candles.dict_from_json(**kwargs)
        df = pd.DataFrame(obj_dict.values(), index=obj_dict.keys()).T
        if kwargs['s'] == 'no_data':
            raise Exception('No price data available for this Ticker')
        else:
            df['t'] = df['t'].apply(lambda x: datetime.fromtimestamp(x))
            df.set_index('t', drop=True, inplace=True)
            df.columns = ['close', 'high', 'low', 'open', 'volume']
            return df


@dataclass
class Trash(Data):
    h: float = None
    l: float = None
    o: float = None
    s: str = None
    v: float = None


class TechnicalIndic(Data):
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    @property
    def object(self):
        return TechnicalIndic.from_json_outer(**self.kwargs).__dict__['kwargs']

    def get(self, frequency: str) -> pd.DataFrame:
        freq = frequency
        df = pd.DataFrame(self.object.values(), index=self.object.keys()).T
        df['t'] = df['t'].apply(lambda x: datetime.fromtimestamp(x))
        df.columns = [indic + '_' + str(freq) if indic not in ['t', 'c'] else indic for indic in df.columns]
        return df.set_index('t', drop=True)


@dataclass
class News(Data):
    t: datetime.timestamp = None
    headline: str = None
    source: str = None
    url: str = None

    @staticmethod
    def get(time: int, **kwargs) -> pd.DataFrame:
        delta = time
        kwargs['t'] = kwargs.pop('datetime')
        obj_dict = News.dict_from_json(**kwargs)
        df = pd.DataFrame([obj_dict.values()], columns=obj_dict.keys())
        df['t'] = datetime.fromtimestamp(df['t']) + timedelta(hours=delta)
        return df.set_index('t', drop=True)


@dataclass
class Financials(Data):
    beta: float = None
    priceRelativeToSP500OneYear: float = None
    OneYearPriceReturnDaily: float = None
    marketCapitalization: int = None

    @staticmethod
    def get(**kwargs) -> pd.DataFrame:
        symbol = kwargs['symbol']
        kwargs = kwargs['metric']
        kwargs['priceRelativeToSP500OneYear'] = kwargs.pop('priceRelativeToS&P50052Week')
        kwargs['OneYearPriceReturnDaily'] = kwargs.pop('52WeekPriceReturnDaily')
        obj_dict = Financials.dict_from_json(**kwargs)
        df = pd.DataFrame([obj_dict.values()], columns=obj_dict.keys(), index=[symbol])
        return df


@dataclass
class Insiders(Data):
    name: str = None
    share: int = None
    change: int = None
    transactionDate: str = None
    transactionPrice: int = None

    @staticmethod
    def get(**kwargs) -> pd.DataFrame:
        obj_dict = Insiders.dict_from_json(**kwargs)
        df = pd.DataFrame([obj_dict.values()], columns=obj_dict.keys())
        if df["transactionPrice"].values != 0:
            return df.set_index('transactionDate', drop=True)
        else:
            name = obj_dict['name']
            date = obj_dict['transactionDate']
            print(f'{date} : {name} had a zero-sum transaction')


@dataclass
class Reco(Data):
    buy: str = None
    hold: str = None
    period: str = None
    sell: str = None
    strongBuy: str = None
    strongSell: str = None

    @staticmethod
    def get(**kwargs) -> pd.DataFrame:
        obj_dict = Reco.dict_from_json(**kwargs)
        df = pd.DataFrame([obj_dict.values()], columns=obj_dict.keys())
        return df.set_index('period', drop=True)


@dataclass
class Earns(Data):
    actual: str = None
    surprisePercent: str = None
    period: str = None

    @staticmethod
    def get(**kwargs) -> pd.DataFrame:
        obj_dict = Earns.dict_from_json(**kwargs)
        df = pd.DataFrame([obj_dict.values()], columns=obj_dict.keys())
        return df.set_index('period', drop=True)


@dataclass
class Sentiment(Data):
    atTime: str = None
    mention: str = None
    score: str = None

    @staticmethod
    def get(**kwargs) -> pd.DataFrame:
        obj_dict = Sentiment.dict_from_json(**kwargs)
        df = pd.DataFrame([obj_dict.values()], columns=obj_dict.keys())
        return df.set_index('atTime', drop=True)