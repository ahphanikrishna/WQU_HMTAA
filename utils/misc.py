from optimization import trading_model as ff
from optimization import initial_strategy


if __name__ == "__main__":
    ticker = "NIFTYBEES.NS"
    index_name = "NIFTY ETF"

    df = initial_strategy.load_data(ticker)
    ff.plot_price_data(df, index_name)
    