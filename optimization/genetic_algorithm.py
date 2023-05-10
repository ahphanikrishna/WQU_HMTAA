import copy
import random
import logging
import datetime
import multiprocessing
import numpy as np
import pandas as pd

from pathlib import Path
from optimization.initial_strategy import STRATEGY, LIMITS, load_data
from optimization import trading_model as ff

logger = logging.getLogger(__name__)

NUM_EVOLUTIONS = 100
TOP_PERC = 0.1
NUM_STRATEGIES = 50


TILL_DATE_FILTER = "2023-01-01"

def get_random_strategy():
    random_strat = copy.deepcopy(STRATEGY)
    random_strat["time_period"]["ADXPeriod"] = random.randint(LIMITS.get("Entry_ADX_period_min"),
                                                              LIMITS.get("Entry_ADX_period_max"))
    random_strat["time_period"]["RSIPeriod"] = random.randint(LIMITS.get("Entry_RSI_period_min"),
                                                              LIMITS.get("Entry_RSI_period_max"))
    random_strat["Entry"]["ADX"]["Value"] = random.randint(LIMITS.get("Entry_ADX_value_min"),
                                                           LIMITS.get("Entry_ADX_value_max"))
    random_strat["Entry"]["RSI"]["Value"] = random.randint(LIMITS.get("Entry_RSI_value_min"),
                                                           LIMITS.get("Entry_RSI_value_max"))
    random_strat["Entry"]["ADX"]["direction"] = random.choice(LIMITS.get("Entry_ADX_direction"))
    random_strat["Entry"]["ADXMove"]["Value"] = random.choice(LIMITS.get("Entry_ADX_move"))
    random_strat["Entry"]["RSI"]["direction"] = random.choice(LIMITS.get("Entry_RSI_direction"))
    random_strat["Entry"]["RSIMove"]["Value"] = random.choice(LIMITS.get("Entry_RSI_move"))

    random_strat["time_period"]["EMAPeriod"] = random.randint(LIMITS.get("Exit_EMA_period_min"),
                                                              LIMITS.get("Exit_EMA_period_max"))

    return random_strat


def create_strategy(population):
    exist = True
    strategy = None
    while exist:
        strategy = get_random_strategy()
        check = [d1 for d1 in population if d1 == strategy]
        if not check:
            exist = False
    return strategy


def create_population(population_size=1000):
    population = []
    for i in range(population_size):
        strategy = create_strategy(population)
        population += [strategy]
    return dict(zip(range(population_size), population))


def cross_over(good_strats_index, population):

    new_strategy = copy.deepcopy(STRATEGY)

    new_strategy["time_period"]["ADXPeriod"] = population[random.choice(good_strats_index)]["time_period"]["ADXPeriod"]
    new_strategy["time_period"]["RSIPeriod"] = population[random.choice(good_strats_index)]["time_period"]["RSIPeriod"]
    new_strategy["Entry"]["ADX"]["Value"] = population[random.choice(good_strats_index)]["Entry"]["ADX"]["Value"]
    new_strategy["Entry"]["RSI"]["Value"] = population[random.choice(good_strats_index)]["Entry"]["RSI"]["Value"]
    new_strategy["Entry"]["ADX"]["direction"] = population[random.choice(good_strats_index)]["Entry"]["ADX"]["direction"]
    new_strategy["Entry"]["ADXMove"]["Value"] = population[random.choice(good_strats_index)]["Entry"]["ADXMove"]["Value"]
    new_strategy["Entry"]["RSI"]["direction"] = population[random.choice(good_strats_index)]["Entry"]["RSI"]["direction"]
    new_strategy["Entry"]["RSIMove"]["Value"] = population[random.choice(good_strats_index)]["Entry"]["RSIMove"]["Value"]
    new_strategy["time_period"]["EMAPeriod"] = population[random.choice(good_strats_index)]["time_period"]["EMAPeriod"]

    return new_strategy


def mutation(strategy, flag):
    if flag == "time_period":
        strategy["time_period"]["ADXPeriod"] = random.randint(LIMITS.get("Entry_ADX_period_min"),
                                                              LIMITS.get("Entry_ADX_period_max"))
        strategy["time_period"]["RSIPeriod"] = random.randint(LIMITS.get("Entry_RSI_period_min"),
                                                              LIMITS.get("Entry_RSI_period_max"))
        strategy["time_period"]["EMAPeriod"] = random.randint(LIMITS.get("Exit_EMA_period_min"),
                                                              LIMITS.get("Exit_EMA_period_max"))
    elif flag == "ADX":
        strategy["Entry"]["ADX"]["Value"] = random.randint(LIMITS.get("Entry_ADX_value_min"),
                                                           LIMITS.get("Entry_ADX_value_max"))
        strategy["Entry"]["ADX"]["direction"] = random.choice(LIMITS.get("Entry_ADX_direction"))
        strategy["Entry"]["ADXMove"]["Value"] = random.choice(LIMITS.get("Entry_ADX_move"))

    elif flag == "RSI":
        strategy["Entry"]["RSI"]["Value"] = random.randint(LIMITS.get("Entry_RSI_value_min"),
                                                           LIMITS.get("Entry_RSI_value_max"))
        strategy["Entry"]["RSI"]["direction"] = random.choice(LIMITS.get("Entry_RSI_direction"))
        strategy["Entry"]["RSIMove"]["Value"] = random.choice(LIMITS.get("Entry_RSI_move"))

    return strategy


def run_genetic_algorithm(ticker):

    # logging handlers
    file = str(Path(__file__).parent) + "/Results/{}_{}.log".format(ticker,
                                                                    datetime.datetime.today().strftime("%Y%m%d"))
    c_handler = logging.StreamHandler()
    logger.addHandler(c_handler)

    f_handler = logging.FileHandler(file)
    logger.addHandler(f_handler)
    logger.setLevel(logging.INFO)


    price_data = load_data(ticker)
    price_data = price_data[price_data['Date'] <= TILL_DATE_FILTER]
    population = create_population(NUM_STRATEGIES)
    population[0] = STRATEGY
    change_perc = np.round((1-TOP_PERC)*NUM_STRATEGIES)
    pool = multiprocessing.Pool(8)

    for i in range(NUM_EVOLUTIONS):
        fitness = np.zeros((NUM_STRATEGIES, 2))
        fitness[:, 0] = np.arange(0, NUM_STRATEGIES)

        args = [(price_data, strategy) for strategy in population.values()]
        results = pool.starmap(ff.fitness_function, args)
        fitness[:, 1] = [-result.get("performance Ratio") for result in results]
        # for j, strategy in population.items():
        #     print(j)
        #     fitness[j, 1] = ff.fitness_function(price_data, strategy).get("Max draw-down")

        ranks = fitness[fitness[:, 1].argsort()]
        logger.info("best result for round {} is with \nobective: {}\n"
                    "strategy: {}\nfitness {}".format(i,
                                                      ranks[-1, 1], population[ranks[-1, 0]].__str__(),
                                                      results[int(ranks[-1, 0])].__str__()))

        good_strats = ranks[int(change_perc):, 0]
        bad_strats = ranks[:int(change_perc), 0]

        # dt = datetime.datetime.today().strftime("%Y%m%d")
        # pd.DataFrame(ranks).to_csv(str(Path(__file__).parent) + "/Results/{}_{}_{}.csv".format(ticker, dt, i),
        #                            index=False)

        # applying cross_over and mutation and random strategy on bad strategies

        splits = np.array_split(bad_strats, 3)

        # cross over
        for index in splits[0]:
            population[index] = cross_over(good_strats, population)

        # Mutation
        for index in splits[1]:
            flag = random.choice(["time_period", "ADX", "RSI"])
            population[index] = mutation(population[index], flag)

        # Random
        for index in splits[1]:
            population[index] = create_strategy(population)

    return population, ranks



if __name__ == "__main__":
    population, ranks = run_genetic_algorithm("^NSEI")
    print(ranks[0])
