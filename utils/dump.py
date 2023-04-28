import os
from sqlalchemy import create_engine

from pathlib import Path
from ..utils.stock_data import TickerData


class TickerDump:
    def __int__(self, ticker_name):
        self.ticker_name = ticker_name
        self.__setup()
        self._load()

    def __setup(self):
        self.engine = create_engine('sqlite:////' + os.path.join(Path(__file__).parent.parent, "db/Data.db"), echo=False)
        self.conn = self.engine.connect()

    def _load(self):
        ticker = TickerData(ticker_name=self.ticker_name, period="10y", interval="1d")
        df = ticker.data()
        df = ticker.get_technical_indicators(df)
        df.to_sql('data_{}'.format(self.ticker_name), con=self.engine)


if __name__ == "__main__":
    dump = TickerDump(ticker_name="^NSEI")

