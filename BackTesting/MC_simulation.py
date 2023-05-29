import pandas as pd
import numpy as np
import pickle
import datetime
import multiprocessing
import matplotlib.pyplot as plt

from pathlib import Path
from optimization import initial_strategy
from optimization import trading_model as ff
from optimization.initial_strategy import STRATEGY

PATH = str(Path(__file__).parent) + "/Results/"
TILL_DATE_FILTER = "2020-01-01"
SIMULATIONS = 1000
INITIAL_AMOUNT = 1E5
DRAW_DOWN_TOL = 0.1


def monte_carlo_brownian_motion(ticker):
    df = initial_strategy.load_data(ticker)

    historical = df[df['Date'] <= TILL_DATE_FILTER].reset_index()
    historical.index = historical['Date']
    historical = historical['Close']

    df = df[df['Date'] > TILL_DATE_FILTER].reset_index()
    n_days = len(df)
    dates = df['Date'].values

    actual = df['Close']
    actual.index = df['Date']

    returns = df['Close'].pct_change()
    sigma = returns.std()
    mu = returns.mean()
    dt = 1

    St = pd.DataFrame(0, index=dates, columns=list(range(1, SIMULATIONS+1)))
    St.iloc[0] = df['Close'].iloc[0]

    for i in range(1, n_days):
        ds_2_s = mu*dt + sigma*np.sqrt(dt)*np.random.randn(SIMULATIONS)
        St.iloc[i] = St.iloc[i-1] + St.iloc[i-1]*ds_2_s

    mc_visualisation(St, actual, historical)
    return St


def mc_visualisation(St, actual, historical):
    fig = plt.figure(figsize=(16,8))
    ax1 = fig.add_subplot(111)

    ax1.plot(historical, 'r', lw=1)
    for i in range(1, SIMULATIONS):
        ax1.plot(St[i], 'b', lw=0.5)

    ax1.plot(actual, 'r', lw=1)
    ax1.set_xlabel("Date", fontsize=20)
    ax1.set_ylabel("Price", fontsize=20)
    ax1.set_title("Monte Carlo Stochastic simulation", fontsize=20)
    dt = datetime.datetime.now().strftime("%Y%m%d%H%M")
    plt.savefig(PATH + "MC_stochastic_paths_{}.jpg".format(dt))
    plt.show(block=False)


def standard_price_data(data):
    data = data.reset_index(drop=False)
    data.columns = ["Date", "Close"]
    data.loc[:, "High"] = data.loc[:, "Close"] * (np.random.rand()-0.5)
    data.loc[:, "Low"] = data.loc[:, "Close"] * (np.random.rand()-0.5)
    return data


def back_testing_mc(price_data, strategy):

    pool = multiprocessing.Pool(16)
    args = [(standard_price_data(price_data[i]), strategy, i, INITIAL_AMOUNT, DRAW_DOWN_TOL) for i in range(1, SIMULATIONS+1)]
    results = pool.starmap(ff.fitness_function, args)
    results = [x for x in results if x.get("Total Returns") != 0]
    fitness = np.zeros((len(results), 4))
    fitness[:, 0] = [result.get("Key") for result in results]
    fitness[:, 1] = [result.get("Total Returns") for result in results]
    fitness[:, 2] = [result.get("performance Ratio") for result in results]
    fitness[:, 3] = [result.get("Max draw-down") if result.get("Max draw-down") != -1e6 else 0 for result in results]

    return fitness


def plot_back_testing_results(fitness_ga, fitness_det):

    fig, axs = plt.subplots(1, 3, figsize=(18, 7), tight_layout=True)

    for i, title in enumerate(["Total Returns", "Objective", "Max Draw-down"]):
        pd.DataFrame(fitness_ga[:, i+1]).plot(kind='density', ax=axs[i], label="Deterministic strategy")
        pd.DataFrame(fitness_det[:, i+1]).plot(kind='density', ax=axs[i], label="GA Optmized")

        mu = max(np.mean(fitness_ga[:, i+1]), np.mean(fitness_det[:, i+1]))
        sigma = max(np.std(fitness_ga[:, i+1]), np.std(fitness_det[:, i+1]))

        axs[i].set_xlim(mu-3*sigma, mu+3*sigma)
        axs[i].set_title(title)
        axs[i].legend(["Deterministic strategy", "GA Optimized"])

    dt = datetime.datetime.now().strftime("%Y%m%d%H%M")
    plt.savefig(PATH + "MC_backtest_distribution_{}.jpg".format(dt))
    plt.show(block=False)


if __name__ == "__main__":
    ticker = "NIFTYBEES.NS"
    mc_price_data = monte_carlo_brownian_motion(ticker)
    ga_strategy = dict(time_period={'ADXPeriod': 16, 'RSIPeriod': 22, 'EMAPeriod': 25},
                        Entry=dict(ADX={'Value': 18, 'Type': 'value', 'direction': 'up'},
                                   RSI={'Value': 54, 'Type': 'value', 'direction': 'up'},
                                   ADXMove={'Value': True, 'Type': bool, 'direction': None},
                                   RSIMove={'Value': True, 'Type': bool, 'direction': None}),
                        Exit=dict(Close={'Value': 'EMA', 'Type': 'column', 'direction': 'down'}))

    ga_fitness = back_testing_mc(mc_price_data, ga_strategy)

    det_fitness = back_testing_mc(mc_price_data, STRATEGY)
    # ga_fitness = picle.load(open(""))
    plot_back_testing_results(ga_fitness, det_fitness)




