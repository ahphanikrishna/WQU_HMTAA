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
from optimization.test_strategy import strategy_test

logger = logging.getLogger(__name__)

NUM_EVOLUTIONS = 100

TOP_PERC = 0.1
NUM_STRATEGIES = 100
INITIAL_AMOUNT = 1E5
OBJECTIVE = "Objective"
MUTATION_PERC = 0.02
CROSS_OVER_PERC = 0.5
DRAW_DOWN_TOL = 0.1

TILL_DATE_FILTER = "2020-01-01"

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


def count_unique_population(population):
    unique_list = []
    for x in population:
        if x not in unique_list:
            unique_list.append(x)

    return unique_list


def strategy_exists(strategy, population):
    check = [d1 for d1 in population if d1 == strategy]
    if check:
        return True
    else:
        return False


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


def run_genetic_algorithm(ticker, index_name, title):

    # logging handlers
    file = str(Path(__file__).parent) + "/Results/{}_{}_{}.log".format(ticker, title,
                                                                    datetime.datetime.now().strftime("%Y%m%d%H%M"))
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
    pool = multiprocessing.Pool(16)

    for i in range(NUM_EVOLUTIONS):
        fitness = np.zeros((NUM_STRATEGIES, 2))
        fitness[:, 0] = np.arange(0, NUM_STRATEGIES)

        args = [(price_data, strategy, INITIAL_AMOUNT, DRAW_DOWN_TOL) for strategy in population.values()]
        results = pool.starmap(ff.fitness_function, args)
        fitness[:, 1] = [result.get(OBJECTIVE) for result in results]

        ranks = fitness[fitness[:, 1].argsort()]
        logger.info("best result for round {} is with \nobective: {}\n"
                    "strategy: {}\nfitness {}".format(i,
                                                      ranks[-1, 1], population[ranks[-1, 0]].__str__(),
                                                      results[int(ranks[-1, 0])].__str__()))

        good_strats = ranks[int(change_perc):, 0]
        bad_strats = ranks[:int(change_perc), 0]

        # applying cross_over and mutation and random strategy on bad strategies

        # splits = np.array_split(bad_strats, 3)
        #
        # # cross over
        # for index in splits[0]:
        #     population[index] = cross_over(good_strats, population)
        #
        # # Mutation
        # for index in splits[1]:
        #     flag = random.choice(["time_period", "ADX", "RSI"])
        #     population[index] = mutation(population[index], flag)
        #
        # # Random
        # for index in splits[1]:
        #     new_strategy = create_strategy(list(population.values()))
        #     population[index] = new_strategy

        # Using random numbers to do crossover and mutation
        for index in bad_strats:
            random_number = random.random()

            if random_number <= MUTATION_PERC:
                flag = random.choice(["time_period", "ADX", "RSI"])
                population[index] = mutation(population[index], flag)
            elif MUTATION_PERC < random_number <= CROSS_OVER_PERC:
                population[index] = cross_over(good_strats, population)
            elif random_number > CROSS_OVER_PERC:
                population[index] = create_strategy(list(population.values()))

        unique_population = count_unique_population(list(population.values()))
        duplicates = len(list(population.values())) - len(unique_population)
        if duplicates > 0:
            logger.info("Duplicates found in population with duplicates number: {}".format(duplicates))

    strategy_test(
        ticker,
        index_name,
        population[ranks[-1, 0]],
        title)
    return population, ranks


if __name__ == "__main__":
    population, ranks = run_genetic_algorithm("NIFTYBEES.NS", "NIFTYBEES ETF", "Performance Optimization and Total Returns")
    print(ranks[0])
