#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  1 19:16:22 2019

@author: Yan
"""

import os 
import matplotlib.pyplot as plt
import numpy as np

parent_path = os.getcwd()
sep = "/" if "sep" in parent_path else '''/'''

#please give the director that contains your conf file
conf_director = "experimental_conf"
conf_path = parent_path + f"{sep}{conf_director}"
conf_files = os.listdir(conf_path)

#where your store ur log information
experimental_result = "experimental_result"
if "experimental_result" not in os.listdir(parent_path):
    os.system(f"mkdir {experimental_result}")
 
logging = f"| tee -a {experimental_result}{sep}"


#add different name for different running
#e.g custom_name = "1"
custom_name = ""

def running():
    for conf_file in conf_files:
        result = conf_file[:conf_file.index(".")] + custom_name + ".log"
        if result in os.listdir(f"{parent_path}{sep}{experimental_result}"):
            os.system(f"rm {experimental_result}{sep}{result}")
        os.system(f"python aixi.py -v {conf_director}{sep}{conf_file} " + logging + result)
        
'''
call running to generate the system log files,
please gives correct director of the conf files,
also gives the director where to store the
system log

'''
        
def read(file):
    cycles = []
    average_rewards = []
    with open(file) as f:
        for line in f.readlines():
            line = line.strip()
            if "cycle:" in line:
                cycles.append(int(line[6:]))
            elif "average reward:" in line:
                average_rewards.append(float(line[15:]))
    if len(cycles) != len(average_rewards):
        return cycles, average_rewards[:-1]
    else:
        return cycles, average_rewards[:-1]

def performance_inrease(file,name):
    cycles,average_rewards = read(file)
    num = int(len(cycles)/10)
    plt.figure(figsize=(9, 6)) 
    plt.plot(cycles,average_rewards,'-',color = "cyan",lw = 2)
    plt.plot(cycles,average_rewards,'D',color = "r", markevery = [i for i in cycles if i%num == 0])
    plt.ylim([0.0, 1.0])
    plt.xlabel('Experience (cycles)')
    plt.ylabel("average reward of per cycle")
    plt.title(f"Learning Scalability of {name}")
    plt.show()
    
performance_inrease("experimental_result/coin_flip.log","coin flip")


def smooth(cycles,average_rewards,num):
    interval = int(len(cycles)/num)
    smoothed_cycles = [cycles[0]]
    smoothed_average_rewards = [average_rewards[0]]
    index = 1
    for epoch in range(num):
        avg_reward = np.mean(average_rewards[index:index+interval])
        index+=interval
        smoothed_cycles.append(index)
        smoothed_average_rewards.append(avg_reward)
        
    return smoothed_cycles,smoothed_average_rewards

def interval_performance_inrease(file,name,num):
    cycles,average_rewards = read(file)
    smoothed_cycles,smoothed_average_rewards = smooth(cycles,average_rewards,num)
    plt.figure(figsize=(9, 6)) 
    plt.plot(smoothed_cycles,smoothed_average_rewards,'-',color = "cyan",lw = 2)
    plt.plot(smoothed_cycles,smoothed_average_rewards,'D',color = "r")
    plt.ylim([0.0, 1.0])
    plt.xlabel('Experience (cycles)')
    plt.ylabel("average reward per cycle")
    plt.title(f"Learning Scalability of {name}")
    plt.show()    
    
interval_performance_inrease("experimental_result/coin_flip.log","coin flip",20)

def compare_performance(files,names,num,compare_name):
    
    plt.figure(figsize=(9, 6)) 
    for index in range(len(files)):
        file  = files[index]
        name = names[index] 
        cycles,average_rewards = read(file)
        smoothed_cycles,smoothed_average_rewards = smooth(cycles,average_rewards,num)
        p = plt.plot(smoothed_cycles,smoothed_average_rewards,'-',lw = 2,label = name)
        plt.plot(smoothed_cycles,smoothed_average_rewards,'D',color = p[0].get_color())
    
    plt.ylim([0.0, 1.0])
    plt.legend(loc="lower right")    
    plt.title(f"Learning Scalability of {compare_name}")
    plt.plot()
        
    
compare_performance(["experimental_result/coin_flip.log","experimental_result/coin_flip_v1.log"],
                    ["coin flip","coin flip compare"],20,"parameter settings for coin flip")                
    
        
        
        
        
        