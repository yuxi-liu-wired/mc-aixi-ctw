#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  4 20:07:34 2019

@author: Yan
"""
from pyaixi.environment import Environment
from pyaixi.environments import *
import inspect 


'''

example of swap between environment, run the command below in terminal
python aixi.py -v conf/kuhn_poker.conf -s extended_tiger,100
you need to specify the time to run second environment and name of second environment
please follow  -s <name of second enviroment,time to run second environment>


'''

def load(environment_title,agent,options):
    
    environment_package_name = "pyaixi.environments." + environment_title
    environment_module = __import__(environment_package_name, globals(), locals(),
                                        [environment_title], 0)
    
    environment_class = None
    environment_classname = ""
    for name, obj in inspect.getmembers(environment_module):
        if hasattr(obj, "__bases__") and 'Environment' in [cls.__name__ for cls in obj.__bases__]:
            environment_class = obj
            environment_classname = name
            break
        
    environment = environment_class()
    options["action-bits"] = environment.action_bits()
    options["observation-bits"] = environment.observation_bits()
    options["percept-bits"] = environment.percept_bits()
    options["reward-bits"] = environment.reward_bits()
    options["max-action"] = environment.maximum_action()
    options["max-observation"] = environment.maximum_observation()
    options["max-reward"] = environment.maximum_reward()
    
    agent.environment = environment
    agent.options = options
    
    print()
    print("++" * 20)
    print('{:^40s}'.format("Changed Enviroment"))
    print("++" * 20)
    print()
    
    return agent,environment