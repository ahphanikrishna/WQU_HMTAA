import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.transforms as mtransforms

from datetime import datetime
from pathlib import Path
from utils.dump import DBLoad
from initial_strategy import STRATEGY

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
    plt.savefig(PATH + index_name + "_technical.jpg")
    plt.show(block=False)


def get_strategy_plot(df, strategy_final, index_name):
    fig, axs = plt.subplots(2, figsize=(20, 6))
    ax2 = axs[0].twinx()
    ax2.plot(df['Date'], df['Close'], label=index_name)
    axs[0].plot(df['Date'], df['RSI'], label='RSI', c='grey')
    axs[0].plot(df['Date'], df['ADX'], label='ADX', c='maroon')
    ax2.plot(df['Date'], df['EMA'], label='EMA')

    trans = mtransforms.blended_transform_factory(axs[0].transData, axs[0].transAxes)

    axs[0].fill_between(df['Date'], 0, 1, where=df.loc[:, "Green"] == 1,
                        facecolor='green', alpha=0.5, transform=trans)

    axs[0].set_title('Deterministic Trading Strategy')
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
    plt.savefig(PATH + index_name + "_strategy.jpg")
    plt.show(block=False)


def strategy_results(ticker, STRATEGY):
    db = DBLoad()
    df = db.load(ticker)

    entry_rule = STRATEGY['Entry']
    c = True
    for i, (key, value) in enumerate(entry_rule.items()):
        if i == 0:
            c = (get_condition(value, key, df))
        else:
            c = c & (get_condition(value, key, df))
    df.loc[:, "Entry"] = np.where(c, 1, 0)
    df.loc[:, "Shift Entry"] = df['Entry'].shift(1)

    exit_rule = STRATEGY['Exit']
    for i, (key, value) in enumerate(exit_rule.items()):
        if i == 0:
            c = (get_condition(value, key, df))
        else:
            c = c & (get_condition(value, key, df))

    df.loc[:, "Exit"] = np.where(c, 1, 0)

    df = hold_regions(df)
    strategy_final, df = get_performance(df)
    return strategy_final, df


