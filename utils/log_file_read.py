import os
import ast
from pathlib import Path
import matplotlib.pyplot as plt
import datetime

PATH = str(Path(__file__).parent.parent) + "/optimization/Results/"


def read_log_files(filename):
    with open(filename, "r") as f:
        log = f.readlines()
    print(log, "\n", len(log))
    fitness_dict = {}
    for i, row in enumerate(log):
        if "fitness" in row:
            row = row.replace("fitness ", "")
            new_row = ast.literal_eval(row)
            fitness_dict[i] = new_row

    return fitness_dict


def plot_objective(fitness):
    fig, axs = plt.subplots(1, 1, figsize=(18, 7), tight_layout=True)
    x_axis = list(fitness.keys())
    y_axis = [fitness[x]["Objective"] for x in list(fitness.keys())]
    y_axis_2 = [fitness[x]["Total Returns"] for x in list(fitness.keys())]
    axs.plot(x_axis, y_axis, label="Objective Function", c='r')
    axs2 = axs.twinx()
    axs2.plot(x_axis, y_axis_2, label="Total Returns")
    axs.set_title('Objective function evolution using GA', fontsize=20)
    axs.set_xlabel('Iteration', fontsize=20)
    axs.set_ylabel("Objective Function", fontsize=20)
    axs2.set_ylabel("Total Returns", fontsize=20)
    axs.tick_params(axis='x', labelsize=20)
    axs.tick_params(axis='y', labelsize=20)
    axs2.tick_params(axis='y', labelsize=20)
    axs.set_xlim(0,100)

    axs.legend(loc=1)
    axs2.legend(loc=0)

    dt = datetime.datetime.now().strftime("%Y%m%d%H%M")
    plt.savefig(PATH + "GA_Evolution_{}.jpg".format(dt))
    plt.show(block=False)


if __name__ == "__main__":
    filename = "NIFTYBEES.NS_Performance Optimization and Total Returns_202305190012.log"
    fitness_dict = read_log_files(os.path.join(PATH, filename))
    plot_objective(fitness_dict)