import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.transforms as mtransforms

import datetime
from pathlib import Path
from utils.stock_data import TechnicalIndicators

PATH = str(Path(__file__).parent) + "/Plots/"


def get_condition(cond_dict, cond_column, df):
    if cond_dict["Type"] is bool:
        ret_val = df[cond_column] == cond_dict["Value"]
    else:
        value = cond_dict["Value"] if cond_dict["Type"] == "value" else df[cond_dict["Value"]]
        if cond_dict["direction"] == "up":
            ret_val = df[cond_column] > value
        else:
            ret_val = df[cond_column] < value
    return ret_val


def hold_regions(df):
    for i in range(len(df)):
        if i > 0:
            if df.loc[i, "Entry"] == 1:
                df.loc[i, "Green"] = 1
            elif df.loc[i, "Exit"] == 1:
                df.loc[i, 'Green'] = 0
            else:
                df.loc[i, 'Green'] = df.loc[i - 1, 'Green']
        else:
            df.loc[i, "Green"] = df.loc[i, "Entry"]
    return df


def get_performance(df):
    entries_list = {}
    exit_list = {}
    n = 0
    m = 0

    for i in range(len(df)):
        if i > 0:
            if df.loc[i, "Green"] - df.loc[i - 1, "Green"] == 1:
                df.loc[i, "Profit Index"] = df.loc[i, "Close"]
                entries_list[n] = df.loc[i, "Close"]
                n = n + 1
            elif df.loc[i, "Green"] - df.loc[i - 1, "Green"] == -1:
                df.loc[i, "Profit Index"] = df.loc[i, "Close"]
                exit_list[m] = df.loc[i, "Close"]
                m = m + 1
            else:
                df.loc[i, "Profit Index"] = 0
        else:
            df.loc[i, "Profit Index"] = 0

    strategy_data = df.loc[df.loc[:, "Profit Index"] > 0, ['Date', 'Close', 'Entry', 'Exit']]

    strategy_entry = strategy_data.loc[strategy_data['Entry'] == 1].reset_index(drop=False)
    strategy_entry.columns = [x + "_Entry" for x in strategy_entry.columns]
    strategy_exit = strategy_data.loc[strategy_data['Exit'] == 1].reset_index(drop=False)
    strategy_exit.columns = [x + "_Exit" for x in strategy_exit.columns]

    strategy_final = pd.concat([strategy_entry, strategy_exit], axis=1)
    strategy_final.loc[:, "Returns"] = strategy_final.loc[:, "Close_Exit"] - strategy_final.loc[:, "Close_Entry"]
    strategy_final.loc[:, "Cumulative Returns"] = strategy_final.loc[:, "Returns"].cumsum()

    return strategy_final, df


def get_technical_plot(df, index_name):
    fig, axs = plt.subplots(2, figsize=(20, 6))
    axs[0].plot(df['Date'], df['Close'], label=index_name)
    axs[0].plot(df['Date'], df['EMA'], label='EMA')

    axs[0].set_title('Prices({}/EMA)'.format(index_name))
    axs[0].legend()

    axs[1].plot(df['Date'], df['RSI'], label='RSI')
    axs[1].plot(df['Date'], df['ADX'], label='ADX')

    axs[1].set_title('RSI and ADX')
    axs[1].set_xlabel('Date')
    axs[1].legend()

    dt = datetime.datetime.now().strftime("%Y%m%d%H%M")
    plt.savefig(PATH + index_name + "_technical_{}.jpg".format(dt))
    plt.show(block=False)


def get_strategy_plot(df, strategy_final, index_name, title="Deterministic Trading"):
    fig, axs = plt.subplots(2, figsize=(20, 6))
    ax2 = axs[0].twinx()
    ax2.plot(df['Date'], df['Close'], label=index_name)
    axs[0].plot(df['Date'], df['RSI'], label='RSI', c='grey')
    axs[0].plot(df['Date'], df['ADX'], label='ADX', c='maroon')
    ax2.plot(df['Date'], df['EMA'], label='EMA')

    trans = mtransforms.blended_transform_factory(axs[0].transData, axs[0].transAxes)

    axs[0].fill_between(df['Date'], 0, 1, where=df.loc[:, "Green"] == 1,
                        facecolor='green', alpha=0.5, transform=trans)

    axs[0].set_title('{} Strategy'.format(title))
    axs[0].set_ylabel('Trading Index (RSI, ADX)')
    axs[0].set_ylabel('Price (Close, EMA)')

    axs[0].legend(loc='upper left')
    ax2.legend()

    axs[1].plot(strategy_final['Date_Entry'], strategy_final['Cumulative Returns'],
                label='Cumulative Returns', c='grey')
    axs[1].plot(strategy_final['Date_Entry'], strategy_final['Returns'], label='Returns', c='maroon')

    axs[1].set_title('Deterministic Trading Strategy Returns')
    axs[1].set_ylabel('Returns')

    axs[1].axhline(y=0, color='k', linestyle='--')

    axs[1].legend(loc='upper left')

    dt = datetime.datetime.now().strftime("%Y%m%d%H%M")
    plt.savefig(PATH + index_name + "_strategy_{}.jpg".format(dt))
    plt.show(block=False)


def strategy_results(df, strategy):

    periods = strategy["time_period"]

    df = TechnicalIndicators().get_technical_indicators(df, periods)

    entry_rule = strategy['Entry']
    c = True
    for i, (key, value) in enumerate(entry_rule.items()):
        if i == 0:
            c = (get_condition(value, key, df))
        else:
            c = c & (get_condition(value, key, df))
    df.loc[:, "Entry"] = np.where(c, 1, 0)
    df.loc[:, "Shift Entry"] = df['Entry'].shift(1)

    exit_rule = strategy['Exit']
    for i, (key, value) in enumerate(exit_rule.items()):
        if i == 0:
            c = (get_condition(value, key, df))
        else:
            c = c & (get_condition(value, key, df))

    df.loc[:, "Exit"] = np.where(c, 1, 0)

    df = hold_regions(df)
    strategy_final, df = get_performance(df)
    return strategy_final, df


def fitness_function(df, strategy):
    strategy_final, df = strategy_results(df, strategy)
    if strategy_final.empty:
        ff = {"Win Ratio": 0.0,
              "Max draw-down": -1e6,
              "performance Ratio": 0.0,
              "Total Returns": 0.0}
    elif np.sum(np.where(strategy_final["Returns"] < 0, strategy_final["Returns"], 0)) == 0.0:
        ff = {"Win Ratio": 0.0,
              "Max draw-down": -1e6,
              "performance Ratio": 0.0,
              "Total Returns": 0.0}
    else:
        ff = {"Win Ratio": np.sum(np.where(strategy_final["Returns"] > 0, 1, 0)) / len(strategy_final),
              "Max draw-down": np.sum(np.where(strategy_final["Returns"] < 0, strategy_final["Returns"], 0)),
              "performance Ratio": strategy_final.loc[strategy_final["Returns"] > 0, "Returns"].sum() / \
                                   strategy_final.loc[strategy_final["Returns"] < 0, "Returns"].sum(),
              "Total Returns": strategy_final["Returns"].sum()}

    ff["Objective"] = -ff["performance Ratio"] * 0.8 + ff["Win Ratio"] * 0.8
    return ff
