import datetime
import pandas as pd
from pathlib import Path

from optimization import trading_model as ff
from optimization import initial_strategy

PATH = str(Path(__file__).parent) + "/Results/"
TILL_DATE_FILTER = "2020-01-01"


def strategy_test(ticker, index_name, strategy, title):
    df = initial_strategy.load_data(ticker)
    df = df[df['Date'] > TILL_DATE_FILTER].reset_index()
    new_df = df.copy()

    if not df.empty:
        fitness = ff.fitness_function(df, strategy)
        strategy_final, df = ff.strategy_results(new_df, strategy)
        for i, j in fitness.items():
            print(i, ' : ', j)

        dt = datetime.datetime.now().strftime("%Y%m%d%H%S")
        with pd.ExcelWriter(PATH + "{}_{}_{}.xlsx".format(index_name, title, dt)) as writer:
            strategy_final.to_excel(writer, sheet_name=title)
            df.to_excel(writer, sheet_name="data")

        ff.get_technical_plot(df, index_name)
        ff.get_strategy_plot(df, strategy_final, index_name, title)


if __name__ == "__main__":
    ticker = "NIFTYBEES.NS"
    index_name = "NIFTY ETF (performance Optimization)"
    strategy = dict(time_period={'ADXPeriod': 28, 'RSIPeriod': 7, 'EMAPeriod': 24},
                    Entry=dict(ADX={'Value': 10, 'Type': 'value', 'direction': 'up'},
                               RSI={'Value': 62, 'Type': 'value', 'direction': 'up'},
                               ADXMove={'Value': True, 'Type': bool, 'direction': None},
                               RSIMove={'Value': True, 'Type': bool, 'direction': None}),
                    Exit= dict(Close={'Value': 'EMA', 'Type': 'column', 'direction': 'down'}))

    title = "Performance Optimization and Total Returns"
    strategy_test(ticker, index_name, strategy, title)