
from optimization import fitness_function as ff

STRATEGY = {
    "Entry":    {
                    "ADXPeriod": 14,
                    "RSIPeriod": 14,
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
                "EMAPeriod": 21,
    }
}

LIMITS = {
    "Entry_ADX_period_min": 7,
    "Entry_ADX_period_max": 31,
    "Entry_ADX_value_min": 0,
    "Entry_ADX_value_max": 100,
    "Entry_ADX_direction": ["up", "down"],
    "Entry_ADX_move": [True, False],
    "Entry_RSI_period_min": 7,
    "Entry_RSI_period_max": 31,
    "Entry_RSI_value_min": 0,
    "Entry_RSI_value_max": 100,
    "Entry_RSI_direction": ["up", "down"],
    "Entry_RSI_move": [True, False],
    "Exit_EMA_period_min": 7,
    "Exit_EMA_period_max": 31,
}


if __name__ == "__main__":
    ticker = "HAL"
    index_name = "Hindustan Aeronautics Ltd"
    strategy_final, df = ff.strategy_results(ticker, STRATEGY)
    ff.get_technical_plot(df, index_name)
    ff.get_strategy_plot(df, strategy_final, index_name)