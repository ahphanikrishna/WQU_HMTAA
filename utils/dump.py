import os
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy import MetaData
from sqlalchemy.orm import declarative_base

from pathlib import Path
from utils.stock_data import TickerData


class TickerDump:
    def __init__(self, ticker_name):
        self.ticker_name = ticker_name
        self.__setup()

    def __setup(self):
        self.engine = create_engine('sqlite:///' + os.path.join(Path(__file__).parent.parent, "db\\Data.db"), echo=False)
        self.conn = self.engine.connect()

    def _dump(self):
        ticker = TickerData(ticker_name=self.ticker_name, period="10y", interval="1d")
        df = ticker.data()
        df = ticker.get_technical_indicators(df)
        if not df.empty:
            print(ticker)
            df.to_sql('data_{}'.format(self.ticker_name), con=self.engine)

    def drop_empty_tables(self):
        print(self.ticker_name)
        base = declarative_base()
        metadata = MetaData()
        metadata.reflect(bind=self.engine)
        table = metadata.tables.get('data_{}'.format(self.ticker_name))
        if table is not None:
            row_count = len(self.conn.execute(table.select()).fetchall())
            if row_count < 1:
                print("Deleting table\n")
                base.metadata.drop_all(self.engine, [table], checkfirst=True)

class DBLoad:
    def __init__(self, db_path=None):
        self.db_path = db_path or os.path.join(Path(__file__).parent.parent, "db\\Data.db")
        self.__setup()

    def __setup(self):
        self.engine = create_engine('sqlite:///' + self.db_path, echo=False)
        self.conn = self.engine.connect()

    def load(self, table_name):
        table_df = pd.read_sql_table(
            "data_{}".format(table_name),
            con=self.engine,
        )
        return table_df


if __name__ == "__main__":
    import pandas as pd
    df = pd.read_csv(os.path.join(Path(__file__).parent.parent, "db\\EQUITY_L.csv"))
    for index, row in df.iloc[1400:, :].iterrows():
        ticker_name = row['SYMBOL']
        dump = TickerDump(ticker_name=ticker_name)
        dump.drop_empty_tables()

