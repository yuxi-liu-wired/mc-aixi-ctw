#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  1 19:16:22 2019

@author: Yan Yang u6169130
         Jiayan Liu u6107041
"""

import os
import time
import matplotlib.pyplot as plt
import numpy as np
import getopt
import sys


def running(conf_files, custom_name, experimental_result, conf_directory, logging):
    """ Generates log files.

        - `conf_files`: List of names of configuration files.
        - `custom_name`: A string added to the ends of log file names.
        - `experimental_result`: Name of the folder with experimental result.
        - `conf_directory`: Name of the folder with configuration files.
        - `logging`: ?
    """

    for conf_file in conf_files:
        # The name of the log file.
        log_file = conf_file[:conf_file.index(".")] + "_" + custom_name + ".log"
        # Remove the log file from a previous run.
        if log_file in os.listdir(f"{parent_path}{sep}{experimental_result}"):
            os.system(f"rm {experimental_result}{sep}{log_file}")

        os.system(
            f"python aixi.py -v {conf_directory}{sep}{conf_file} " + logging + log_file)


def read(file, reward):
    cycles = []
    average_rewards = []
    with open(file) as f:
        last_line = None
        for line in f.readlines():
            line = line.strip()

            if "cycle:" in line:
                cycles.append(int(line[6:]))

                if reward:
                    average_rewards.append(float(last_line.split(",")[2]))

            elif not reward and "average reward:" in line:
                average_rewards.append(float(line[15:]))

            last_line = line
    if len(cycles) != len(average_rewards):
        return cycles, average_rewards[:-1]
    else:
        return cycles, average_rewards


def performance_increase(file, name, reward):
    """ Graphs the performance increase.

        - `file`: .
        - `name`: Name of environment being studied
        - `reward`: Boolean for something??
    """

    cycles, average_rewards = read(file, reward)
    num = int(len(cycles) / 10)
    plt.figure(figsize=(9, 6))
    plt.plot(cycles, average_rewards, '-', color="cyan", lw=2)
    plt.plot(cycles, average_rewards, 'D', color="r",
             markevery=[i for i in cycles if i % num == 0])
    # plt.ylim([0.0, 1.0])
    plt.xlabel('Experience (cycles)')
    plt.ylabel("average reward of per cycle")
    plt.title(f"Learning Scalability of {name}")
    plt.show()


def smooth(cycles, average_rewards, num):
    """ TODO

        - `cycles`: .
        - `average_rewards`:
        - `num`:
    """

    interval = int(len(cycles) / num)
    smoothed_cycles = [cycles[0]]
    smoothed_average_rewards = [average_rewards[0]]
    index = 1
    for epoch in range(num):
        avg_reward = np.mean(average_rewards[index:index + interval])
        index += interval
        smoothed_cycles.append(index)
        smoothed_average_rewards.append(avg_reward)

    return smoothed_cycles, smoothed_average_rewards


def interval_performance_increase(file, name, num, reward):
    """ Graphs the performance increase during an interval of time(? TODO: check).

        - `file`: .
        - `name`:
        - `num`:
        - `reward`:
    """

    cycles, average_rewards = read(file, reward)
    smoothed_cycles, smoothed_average_rewards = smooth(
        cycles, average_rewards, num)
    plt.figure(figsize=(9, 6))
    plt.plot(smoothed_cycles, smoothed_average_rewards,
             '-', color="cyan", lw=2)
    plt.plot(smoothed_cycles, smoothed_average_rewards, 'D', color="r")
    # plt.ylim([0.0, 1.0])
    plt.xlabel('Experience (cycles)')
    plt.ylabel("average reward per cycle")
    plt.title(f"Learning Scalability of {name}")
    plt.show()


def compare_performance(files, names, num, compare_name, reward):
    """ Compares performance increase between two TODO

        - `files`: .
        - `names`:
        - `num`:
        - `compare_name`:
        - `reward`:
    """

    plt.figure(figsize=(9, 6))
    for index in range(len(files)):
        file = files[index]
        name = names[index]
        cycles, average_rewards = read(file, reward)
        smoothed_cycles, smoothed_average_rewards = smooth(
            cycles, average_rewards, num)
        p = plt.plot(smoothed_cycles, smoothed_average_rewards,
                     '-', lw=2, label=name)
        plt.plot(smoothed_cycles, smoothed_average_rewards,
                 'D', color=p[0].get_color())

    # plt.ylim([0.0, 1.0])
    plt.legend(loc="lower right")
    plt.title(f"Learning Scalability of {compare_name}")
    plt.plot()
    plt.show()


parent_path = os.getcwd()
sep = "/" if "sep" in parent_path else '''/'''


default_options = {}
default_options["experimental_result"] = "experimental_result"
default_options["conf_directory"] = "experimental_conf"
default_options["custom_name"] = str(time.time())
default_options["interval"] = 50
default_options["type_of_reward"] = "reward"

command_line_options = {}


def main(argv):
    try:
        opts, args = getopt.gnu_getopt(
            argv,
            'e:c:p:i:v:n:g:t:',
            ['experimental_result=', 'conf_directory=',
             'performance_increase_graph=', 'interval_performance_increase_graph=',
             'compare_performance_graph=', 'custom_name=', 'interval=', "type_of_reward"]
        )
        for opt, arg in opts:

            if opt == '--help':
                usage()

            if opt in ('-e', '--experimental_result'):
                command_line_options["experimental_result"] = str(arg)
                continue

            if opt in ('-c', '--conf_directory'):
                command_line_options["conf_directory"] = str(arg)
                continue

            if opt in ('-p', '--performance_increase_graph'):
                command_line_options["performance_increase"] = arg.split("~")
                continue

            if opt in ('-i', '--interval_performance_increase_graph'):
                command_line_options["interval_performance_increase"] = arg.split("~")
                continue

            if opt in ('-v', '--compare_performance_graph'):
                command_line_options["compare_performance"] = arg.split("~")
                continue

            if opt in ('-n', '--custom_name'):
                command_line_options["custom_name"] = str(arg)
                continue

            if opt in ('-g', '--interval'):
                command_line_options["interval"] = int(arg)
                continue

            if opt in ('-t', '--type_of_reward'):
                command_line_options["type_of_reward"] = str(arg)
                continue

    except getopt.GetoptError as e:
        usage()

    # directory of configuration files
    if "conf_directory" in command_line_options:
        conf_directory = command_line_options["conf_directory"]
    else:
        conf_directory = default_options["conf_directory"]

    conf_path = parent_path + f"{sep}{conf_directory}"
    conf_files = [f for f in os.listdir(conf_path) if f.endswith(".conf")]

    # directory of output log files
    if "experimental_result" in command_line_options:
        experimental_result = command_line_options["experimental_result"]
    else:
        experimental_result = default_options["experimental_result"]

    if "experimental_result" not in os.listdir(parent_path):
        os.system(f"mkdir {experimental_result}")

    if "custom_name" in command_line_options:
        custom_name = command_line_options["custom_name"]
    else:
        custom_name = default_options["custom_name"]

    if "interval" in command_line_options:
        interval = command_line_options["interval"]
    else:
        interval = default_options["interval"]

    if "running" in command_line_options and command_line_options["running"]:
        logging = f"| tee -a {experimental_result}{sep}"
        running(conf_files, custom_name,
                experimental_result, conf_directory, logging)

    # TODO: what is this for
    reward = True
    if "type_of_reward" in command_line_options:
        if command_line_options["type_of_reward"] != default_options["type_of_reward"]:
            reward = False

    if "performance_increase" in command_line_options:
        path = command_line_options["performance_increase"][0]
        # "experimental_result/coin_flip.log"
        name = command_line_options["performance_increase"][1]
        # "coin flip"
        performance_increase(path, name, reward)

    if "interval_performance_increase" in command_line_options and command_line_options["interval_performance_increase"]:
        path = command_line_options["interval_performance_increase"][0]
        # "experimental_result/coin_flip.log"
        name = command_line_options["interval_performance_increase"][1]
        # "coin flip"
        interval_performance_increase(path, name, interval, reward)

    if "compare_performance" in command_line_options and command_line_options["compare_performance"]:
        directory = command_line_options["compare_performance"][0]
        # ["experimental_result/coin_flip.log","experimental_result/coin_flip_v1.log"]
        paths = sorted([f"{directory}{sep}{f}" for f in os.listdir(
            directory) if f.endswith(".log")])
        print(command_line_options["compare_performance"])
        names = eval(command_line_options["compare_performance"][1])
        title = str(command_line_options["compare_performance"][2])
        # ["coin flip","coin flip compare"]
        compare_performance(paths, names, interval,
                            f"parameter settings for {title}", reward)


def usage():
    message = "Usage: python experimental_script.py [-e | --experimental_result <directory name of experimental result log files>]" + os.linesep + \
              "                                     [-c | --conf_directory <directory name of configuration files>]" + os.linesep + \
              "                                     [-p | --performance_increase_graph]" + os.linesep + \
              "                                     [-i | --interval_performance_increase_graph]" + os.linesep + \
              "                                     [-v | --compare_performance_graph]" + os.linesep + \
              "                                     [-n | --custom_name <suffix string of log files>]" + os.linesep + \
              "                                     [-g | --interval]" + os.linesep +\
              "Usage examples:" + os.linesep +\
              '''     python experimental_script.py  -c experimental_conf -n test -e experimental_result''' + os.linesep +\
              '''     python experimental_script.py  -v "experimental_result~['coin flip','coin flip compare']~coin flip" -g 10 ''' + os.linesep +\
              '''     python experimental_script.py  -i "experimental_result/coin_flip.log~coin flip" -g 10''' + os.linesep +\
              '\n' +\
              "     The performance increase function expects 2 inputs, file and tile, separated by '~'" + os.linesep +\
              "     Including any space without quotation marks '' may lead to an error. " + os.linesep +\
              "     To output performance comparison graph, input the labels of the log file in alphabetical order" + os.linesep

    sys.stderr.write(message)
    sys.exit(2)


if __name__ == "__main__":
    main(sys.argv[1:])
