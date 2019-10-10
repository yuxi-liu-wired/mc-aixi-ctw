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



def running(conf_files,custom_name,experimental_result,conf_directory,logging):
    
    '''
    call running to generate the system log files,
    please gives correct directory of the conf files,
    also gives the directory where to store the
    system log

    '''
    
    for conf_file in conf_files:
        result = conf_file[:conf_file.index(".")] + "_" + custom_name + ".log"
        if result in os.listdir(f"{parent_path}{sep}{experimental_result}"):
            os.system(f"rm {experimental_result}{sep}{result}")
        os.system(f"python aixi.py -v {conf_directory}{sep}{conf_file} " + logging + result)
        
        
        
        
def read(file,reward):
    '''
    read the log file and specify which type of reward to read
    if reward is true, then we read reward,
    otherwise we read average reward.
    
    '''
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

def performance_inrease(file,name,reward):
    '''
    perfomrmance inrease graph
    
    '''
    cycles,average_rewards = read(file,reward)
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
    '''
    calculate time interval based average reward
    
    '''
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

def interval_performance_inrease(file,name,num,reward):
    
    '''
    Generate graph about change of reward based on time interval.
    
    '''
    
    cycles,average_rewards = read(file,reward)
    smoothed_cycles,smoothed_average_rewards = smooth(cycles,average_rewards,num)
    plt.figure(figsize=(9, 6)) 
    plt.plot(smoothed_cycles,smoothed_average_rewards,'-',color = "cyan",lw = 2)
    plt.plot(smoothed_cycles,smoothed_average_rewards,'D',color = "r")
    #plt.ylim([0.0, 1.0])
    plt.xlabel('Experience (cycles)')
    plt.ylabel("average reward per cycle")
    plt.title(f"Learning Scalability of {name}")
    plt.show()    


def compare_performance(files,names,num,compare_name,reward):
    
    '''
    Generate the graph with based on list of conf files. In order to find out 
    the performance change with respect to different configurations.
    
    '''
    
    plt.figure(figsize=(9, 6)) 
    for index in range(len(files)):
        file  = files[index]
        name = names[index] 
        cycles,average_rewards = read(file,reward)
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
default_options["conf_directory"]                 =  "experimental_conf"
default_options["custom_name"]                   =  str(time.time())
default_options["interval"]                      =  50
default_options["type_of_reward"]                =  "reward"
    
command_line_options = {}
    

def main(argv):
    
    '''
    experimental_result: The folder to store the experimental result. 
        The script will create it if there doesn't existes one.
        And, all information is stored as log file.  
    
    conf_director: The folder contains the different configure files.
        Only the file endup with ".conf" will be experimented.
    
    performance_inrease_graph: Reading the specifed log file, and generate a single graph about reward.
        The format for setting the parameter is < log file >$\text{~}$<'title of the graph'>  
    
    interval_performance_inrease_graph: Reading the specifed log file, 
        and generate a single smoothed graph about the average reward.
        The interval can be set by using interval parameter. 
        And, the format for setting the parameter is 
        < log file >$\text{~}$<'title of the graph'>
    
    compare_performance_graph: By supplying the director, it will reading a list of log file. 
        Then, generate the graph for them. The format to giving the value is 
        < where store the log files >$\text{~}$<"['name of labels',]">$\text{~}$<'title of graph'>. 
        Be careful, the order for the name of labels need to corresponds with the alphabeta order of log files.
    
    custom_name: The log file for different configure files wil be stored as the name of configure file plus the custom_name. 
        if no custom name is supplied, the current time will be considered as custom name. 
    
    interval: In order to smooth the history reward, the interval need to be supplied.
        The default value will be 50.
    
    type of reward: Used to indicate whether we should read average reward or reward from the log file.
    
    '''

    try:
        opts, args = getopt.gnu_getopt(
                    argv,
                    'e:c:p:i:v:n:g:t:',
                    ['experimental_result=', 'conf_directory=',
                     'performance_inrease_graph=','interval_performance_inrease_graph=',
                     'compare_performance_graph=','custom_name=','interval=',"type_of_reward",]
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
            
            
            if opt in ('-p', '--performance_inrease_graph'):
                command_line_options["performance_inrease"] = arg.split("~")
                if len(arg.split("~"))!= 2:
                    raise SystemExit("incorrect input")
                continue
            
            if opt in ('-i', '--interval_performance_inrease_graph'):
                command_line_options["interval_performance_inrease"] = arg.split("~")
                if len(arg.split("~"))!= 2:
                    raise SystemExit("incorrect input")
                continue
            
            if opt in ('-v', '--compare_performance_graph'):
                command_line_options["compare_performance"] = arg.split("~")
                if len(arg.split("~"))!= 3:
                    raise SystemExit("incorrect input")
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
        
    
    #please give the directory that contains your conf file

    if "conf_directory" in command_line_options:
        conf_directory = command_line_options["conf_directory"]
    
    else:
        conf_directory = default_options["conf_directory"]
    
    conf_path = parent_path + f"{sep}{conf_directory}"
    conf_files = [f for f in os.listdir(conf_path) if f.endswith(".conf")]
    
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
        
        
    if "experimental_result" in command_line_options:
        logging = f"| tee -a {experimental_result}{sep}"
        running(conf_files,custom_name,experimental_result,conf_directory,logging)
        
    if "type_of_reward" in command_line_options:
        
        if command_line_options["type_of_reward"] == default_options["type_of_reward"]:
            reward = True
        else:
            #put in any string to get average reward instead of reward
            reward = False
        
    else:
        reward = True
    
    if "performance_inrease" in command_line_options:
        path = command_line_options["performance_inrease"][0]
        #"experimental_result/coin_flip.log"
        name = command_line_options["performance_inrease"][1]
        #"coin flip"
        performance_inrease(path,name,reward)
        
    
    if "interval_performance_inrease" in command_line_options and command_line_options["interval_performance_inrease"]:
        
        path = command_line_options["interval_performance_inrease"][0]
        #"experimental_result/coin_flip.log"
        name = command_line_options["interval_performance_inrease"][1]
        #"coin flip"
        
        interval_performance_inrease(path,name,interval,reward)
        
    
    if "compare_performance" in command_line_options and command_line_options["compare_performance"]: 
        
        director = command_line_options["compare_performance"][0]
        #["experimental_result/coin_flip.log","experimental_result/coin_flip_v1.log"]
        paths = sorted([f"{director}{sep}{f}" for f in os.listdir(director) if f.endswith(".log")])
        names = eval(command_line_options["compare_performance"][1])
        title = str(command_line_options["compare_performance"][2])
        #["coin flip","coin flip compare"]
        compare_performance(paths,names,interval,f"parameter settings for {title}",reward)      
        
def usage():
    message = "Usage: python experimental_script.py [-e | --experimental_result" + os.linesep + \
              "                                     [-c | --conf_directory" + os.linesep + \
              "                                     [-p | --performance_inrease_graph" + os.linesep + \
              "                                     [-i | --interval_performance_inrease_graph" + os.linesep + \
              "                                     [-v | --compare_performance_graph" + os.linesep + \
              "                                     [-n | --custom_name" + os.linesep + \
              "                                     [-g | --interval" + os.linesep +\
              "                                     [-t | --type_of_reward" + os.linesep +\
              "Example of Usage" + os.linesep +\
              '''     python experimental_script.py  -c experimental_conf -n test -e experimental_result''' + + os.linesep +\
              '''     python experimental_script.py  -v experimental_result~"['coin flip','coin flip compare']"~'coin flip' -g 10 ''' + os.linesep +\
              '''     python experimental_script.py  -i 'experimental_result/coin_flip.log'~'coin flip' -g 10 ''' + os.linesep +\
              '''     python experimental_script.py  -p experimental_result/coin_flip.log~'coin flip' -t avg '''  + os.linesep +\
              "     The performance increase function expect 2 inputs, file and tile, please using ~ to split your inputs" + os.linesep +\
              "     Include any space without using '' may leads a error. " + os.linesep +\
              "     For the  compare performance graph please given the names of label correspond with the alphabeta order of log file" + os.linesep
              
              
    sys.stderr.write(message)
    sys.exit(2)

if __name__ == "__main__":
    main(sys.argv[1:])
    
        
        
        