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



def running(conf_files,custom_name,experimental_result,conf_director,logging):
    
    '''
    call running to generate the system log files,
    please gives correct director of the conf files,
    also gives the director where to store the
    system log

    '''
    
    for conf_file in conf_files:
        result = conf_file[:conf_file.index(".")] + "_" + custom_name + ".log"
        if result in os.listdir(f"{parent_path}{sep}{experimental_result}"):
            os.system(f"rm {experimental_result}{sep}{result}")
        os.system(f"python aixi.py -v {conf_director}{sep}{conf_file} " + logging + result)
        
        
        
        
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
        return cycles, average_rewards

def performance_inrease(file,name):
    cycles,average_rewards = read(file)
    num = int(len(cycles)/10)
    plt.figure(figsize=(9, 6)) 
    plt.plot(cycles,average_rewards,'-',color = "cyan",lw = 2)
    plt.plot(cycles,average_rewards,'D',color = "r", markevery = [i for i in cycles if i%num == 0])
    #plt.ylim([0.0, 1.0])
    plt.xlabel('Experience (cycles)')
    plt.ylabel("average reward of per cycle")
    plt.title(f"Learning Scalability of {name}")
    plt.show()
    



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
    #plt.ylim([0.0, 1.0])
    plt.xlabel('Experience (cycles)')
    plt.ylabel("average reward per cycle")
    plt.title(f"Learning Scalability of {name}")
    plt.show()    


def compare_performance(files,names,num,compare_name):
    
    plt.figure(figsize=(9, 6)) 
    for index in range(len(files)):
        file  = files[index]
        name = names[index] 
        cycles,average_rewards = read(file)
        smoothed_cycles,smoothed_average_rewards = smooth(cycles,average_rewards,num)
        p = plt.plot(smoothed_cycles,smoothed_average_rewards,'-',lw = 2,label = name)
        plt.plot(smoothed_cycles,smoothed_average_rewards,'D',color = p[0].get_color())
    
    #plt.ylim([0.0, 1.0])
    plt.legend(loc="lower right")    
    plt.title(f"Learning Scalability of {compare_name}")
    plt.plot()
    plt.show()
        
parent_path = os.getcwd()
sep = "/" if "sep" in parent_path else '''/'''


default_options = {}
default_options["experimental_result"]           = "experimental_result"
default_options["conf_director"]                 =  "experimental_conf"
default_options["custom_name"]                   =  str(time.time())
default_options["interval"]                      =  50
    
command_line_options = {}
    

def main(argv):

    try:
        opts, args = getopt.gnu_getopt(
                    argv,
                    'e:c:r:p:i:v:n:g:',
                    ['experimental_result=', 'conf_director=','running_experiments=',
                     'performance_inrease_graph=','interval_performance_inrease_graph=',
                     'compare_performance_graph=','custom_name=','interval=']
                    )
        for opt, arg in opts:
            
            if opt == '--help':
                usage()
            
            if opt in ('-e', '--experimental_resul'):
                command_line_options["experimental_resul"] = str(arg)
                continue
            
            if opt in ('-c', '--conf_director'):
                command_line_options["conf_director"] = str(arg)
                continue
            
            
            if opt in ('-r', '--running_experiments'):
                command_line_options["running"] = eval(arg)
                continue
            
            if opt in ('-p', '--performance_inrease_graph'):
                command_line_options["performance_inrease"] = arg.split("~")
                continue
            
            if opt in ('-i', '--interval_performance_inrease_graph'):
                command_line_options["interval_performance_inrease"] = arg.split("~")
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
            
            
    except getopt.GetoptError as e:
        usage()
        
    
    #please give the director that contains your conf file

    if "conf_director" in command_line_options:
        conf_director = command_line_options["conf_director"]
    
    else:
        conf_director = default_options["conf_director"]
    
    conf_path = parent_path + f"{sep}{conf_director}"
    conf_files = os.listdir(conf_path)
    
    #where your store ur log information
    if "experimental_result" in command_line_options:
        experimental_result = command_line_options["experimental_result"]
    
    else:
        experimental_result = default_options["experimental_result"]
    
    if "experimental_result" not in os.listdir(parent_path):
        os.system(f"mkdir {experimental_result}")
        
        
    #add different name for different running
    #e.g custom_name = "1"
    
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
        running(conf_files,custom_name,experimental_result,conf_director,logging)
        
    
    if "performance_inrease" in command_line_options:
        path = command_line_options["performance_inrease"][0]
        #"experimental_result/coin_flip.log"
        name = command_line_options["performance_inrease"][1]
        #"coin flip"
        performance_inrease(path,name)
        
    
    if "interval_performance_inrease" in command_line_options and command_line_options["interval_performance_inrease"]:
        
        path = command_line_options["interval_performance_inrease"][0]
        #"experimental_result/coin_flip.log"
        name = command_line_options["interval_performance_inrease"][1]
        #"coin flip"
        
        interval_performance_inrease(path,name,interval)
        
    
    if "compare_performance" in command_line_options and command_line_options["compare_performance"]: 
        
        director = command_line_options["compare_performance"][0]
        #["experimental_result/coin_flip.log","experimental_result/coin_flip_v1.log"]
        paths = sorted([f"{director}{sep}{f}" for f in os.listdir(director) if f.endswith(".log")])
        names = eval(command_line_options["compare_performance"][1])
        title = str(command_line_options["compare_performance"][2])
        #["coin flip","coin flip compare"]
        compare_performance(paths,names,interval,f"parameter settings for {title}")      
        
def usage():
    message = "Usage: python experimental_script.py [-e | --experimental_resul" + os.linesep + \
              "                                     [-c | --conf_director" + os.linesep + \
              "                                     [-r | --running_experiments" + os.linesep + \
              "                                     [-p | --performance_inrease_graph" + os.linesep + \
              "                                     [-i | --interval_performance_inrease_graph" + os.linesep + \
              "                                     [-v | --compare_performance_graph" + os.linesep + \
              "                                     [-n | --custom_name" + os.linesep + \
              "                                     [-g | --interval" + os.linesep +\
              "Example of Usage" + os.linesep +\
              '''     python experimental_script.py -r True -c experimental_conf -n test -e experimental_result''' + + os.linesep +\
              '''     python experimental_script.py  -v experimental_result~"['coin flip','coin flip compare']"~'coin flip' -g 10 ''' + os.linesep +\
              '''     python experimental_script.py  -i 'experimental_result/coin_flip.log'~'coin flip' -g 10''' + os.linesep +\
              "     The performance increase function expect 2 inputs, file and tile, please using ~ to split your inputs" + os.linesep +\
              "     Include any space without using '' may leads a error. " + os.linesep +\
              "     For the  compare performance graph please given the names of label correspond with the alphabeta order of log file" + os.linesep
              
              
    sys.stderr.write(message)
    sys.exit(2)

if __name__ == "__main__":
    main(sys.argv[1:])
    
        
        
        