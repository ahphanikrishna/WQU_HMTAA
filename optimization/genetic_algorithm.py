import copy
import random
from optimization.initial_strategy import STRATEGY, LIMITS


def get_random_strategy():
    random_strat = copy.deepcopy(STRATEGY)
    random_strat["Entry"]["ADXPeriod"] = random.randint(LIMITS.get("Entry_ADX_period_min"),
                                                        LIMITS.get("Entry_ADX_period_max"))
    random_strat["Entry"]["RSIPeriod"] = random.randint(LIMITS.get("Entry_RSI_period_min"),
                                                        LIMITS.get("Entry_RSI_period_max"))
    random_strat["Entry"]["ADX"]["Value"] = random.randint(LIMITS.get("Entry_ADX_value_min"),
                                                           LIMITS.get("Entry_ADX_value_max"))
    random_strat["Entry"]["RSI"]["Value"] = random.randint(LIMITS.get("Entry_RSI_value_min"),
                                                           LIMITS.get("Entry_RSI_value_max"))
    random_strat["Entry"]["ADX"]["direction"] = random.choice(LIMITS.get("Entry_ADX_direction"))
    random_strat["Entry"]["ADXMove"]["Value"] = random.choice(LIMITS.get("Entry_ADX_move"))
    random_strat["Entry"]["RSI"]["direction"] = random.choice(LIMITS.get("Entry_RSI_direction"))
    random_strat["Entry"]["RSIMove"]["Value"] = random.choice(LIMITS.get("Entry_RSI_move"))

    random_strat["Exit"]["EMAPeriod"] = random.randint(LIMITS.get("Exit_EMA_period_min"),
                                                       LIMITS.get("Exit_EMA_period_max"))

    return random_strat


def create_strategy(population):
    exist = True
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
    return population


if __name__ == "__main__":
    population = create_population()
    print(population[1])
