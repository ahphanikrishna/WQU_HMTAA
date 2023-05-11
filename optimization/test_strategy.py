from optimization import trading_model as ff
from optimization import initial_strategy


def strategy_test(ticker, index_name, strategy):
    df = initial_strategy.load_data(ticker)
    new_df = df.copy()
    if not df.empty:
        fitness = ff.fitness_function(df, strategy)
        strategy_final, df = ff.strategy_results(new_df, strategy)
        for i, j in fitness.items():
            print(i, ' : ', j)
        ff.get_technical_plot(df, index_name)
        ff.get_strategy_plot(df, strategy_final, index_name)


if __name__ == "__main__":
    ticker = "^NSEI"
    index_name = "NIFTY"
    strategy = dict(time_period={'ADXPeriod': 14, 'RSIPeriod': 11, 'EMAPeriod': 29},
                    Entry=dict(ADX={'Value': 8, 'Type': 'value', 'direction': 'up'},
                               RSI={'Value': 71, 'Type': 'value', 'direction': 'up'},
                               ADXMove={'Value': True, 'Type': bool, 'direction': None},
                               RSIMove={'Value': True, 'Type': bool, 'direction': None}),
                    Exit= dict(Close={'Value': 'EMA', 'Type': 'column', 'direction': 'down'}))

    strategy_test(ticker, index_name, strategy)