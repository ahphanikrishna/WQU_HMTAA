import pandas as pd
from utils.dump import DBLoad, TickerDump
from optimization import trading_model as ff

STRATEGY = {
    "time_period":   {
                    "ADXPeriod": 14,
                    "RSIPeriod": 14,
                    "EMAPeriod": 21,
                },
    "Entry":    {

                    "ADX": {
                            "Value": 20,
                            "Type": "value",
                            "direction": "up",
                            },
                    "RSI": {
                            "Value": 60,
                            "Type": "value",
                            "direction": "up",
                            },
                    "ADXMove": {
                                "Value": True,
                                "Type": bool,
                                "direction": None,
                                },
                    "RSIMove": {
                                "Value": True,
                                "Type": bool,
                                "direction": None,
                                },
                    },
    "Exit": {
                "Close": {
                        "Value": "EMA",
                        "Type": "column",
                        "direction": "down",
                        },
    }
}

LIMITS = {
    "Entry_ADX_period_min": 7,
    "Entry_ADX_period_max": 31,
    "Entry_ADX_value_min": 5,
    "Entry_ADX_value_max": 40

    ,
    "Entry_ADX_direction": ["up"],
    "Entry_ADX_move": [True,False],
    "Entry_RSI_period_min": 7,
    "Entry_RSI_period_max": 31,
    "Entry_RSI_value_min": 10,
    "Entry_RSI_value_max": 80,
    "Entry_RSI_direction": ["up","down"],
    "Entry_RSI_move": [True,False],
    "Exit_EMA_period_min": 7,
    "Exit_EMA_period_max": 31,
}


def load_data(ticker):
    db = DBLoad()
    df = pd.DataFrame()
    if db.check_table(ticker):
        df = db.load(ticker)
    else:
        dump = TickerDump(ticker_name="^NSEI")
        dump.dump()
        if db.check_table(ticker):
            df = db.load(ticker)
    return df

if __name__ == "__main__":
    ticker = "^NSEI"
    index_name = "NIFTY"

    df = load_data(ticker)
    if not df.empty:
        fitness = ff.fitness_function(df, STRATEGY)
        for i, j in fitness.items():
            print(i, ' : ', j)
        # ff.get_technical_plot(df, index_name)
        # ff.get_strategy_plot(df, strategy_final, index_name)