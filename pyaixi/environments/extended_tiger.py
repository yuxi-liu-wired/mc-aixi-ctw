#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 27 09:00:01 2019

@author: jiayanliu, Wenxi Wu
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import random
import sys
import numpy as np

PROJECT_ROOT = os.path.realpath(os.path.join(os.pardir, os.pardir))
sys.path.insert(0, PROJECT_ROOT)

from pyaixi import environment, util

description = 'extended_tiger.txt'

tiger_action_enum = util.enum('stand','listen','open_left_door','open_right_door')
print(tiger_action_enum)
tiger_observation_enum = util.enum('left','right','void')
tiger_state_enum = util.enum('sitting', 'standing')

sitting = tiger_state_enum.sitting
standing = tiger_state_enum.standing

stand = tiger_action_enum.stand
listen = tiger_action_enum.listen
open_left = tiger_action_enum.open_left_door
open_right = tiger_action_enum.open_right_door

left = tiger_observation_enum.left
right = tiger_observation_enum.right
void = tiger_observation_enum.void

class ExtendedTiger(environment.Environment):
    """ 
        extended tiger position prediction, a tiger behind in a door, player 
        is asking to open one of the door(left or right), before open either 
        door, player is sitting on a chair, and can listen the noise made by 
        tiger, but it has a probility of 0.85 that player get correct observation.

        Domain characteristics:

        - environment: "extended_tiger"
        - maximum action: 4 (2 bit)
        - maximum observation: 3 (2 bit)
        - maximum reward: 256 (8 bit)
    """

    """
    default ptobability of correct observation given by action listenning
    """
    default_probability = 0.85

    # Instance methods.

    def __init__(self, options = {}):
        """ Construct the CoinFlip environment from the given options.

             - `options` is a dictionary of named options and their values.

            The following options in `options` are optional:
        """

        # Set up the base environment.
        environment.Environment.__init__(self, options = options)

        # Defines the acceptable action values.
        self.valid_actions = list(tiger_action_enum.keys())

        # Defines the acceptable observation values.
        self.valid_observations = list(tiger_observation_enum.keys())
        
        self.valid_rewards = range(2**8)
        # Set an initial percept.
        self.reward = 128 #given initial reward with 128
        self.is_finished = False
        self.state = sitting
        self.observation = void
        self.tiger = left if random.randint(0,1) == 1 else right
    # end def


    def perform_action(self, action):
        """ Receives the agent's action and calculates the new environment percept.
        """
        assert self.is_valid_action(action)
        # Save the action.
        self.action = action
        print("perform action", action)
        tmp_reward = 0
        tmp_observation = void
        if self.state == sitting:  
            if action == stand:
                self.reward -= 1  #perform stand, when sitting given reward -1
                self.state = standing
                tmp_reward = self.reward
            elif action == listen: #perform lsiten, when sitting given reward -1
                self.reward -= 1
                tmp_reward = self.reward
                if (random.random() <= self.default_probability):
                    self.observation = self.tiger
                else:
                    if self.tiger == left:
                        self.observation = right
                        tmp_observation = void
                    else:
                        self.observation = left
                        tmp_observation = void
            else: #other invalid action given reward -10
                self.reward -= 10
                tmp_reward = self.reward
        else:
            if action == open_left:  
                if self.tiger == left:
                    self.reward -= 100 #open door with tiger when standing given reward -100
                else:
                    self.reward += 30  #open door with gold when standing given reward +30
                tmp_reward = self.reward
                tmp_observation = self.observation
                self.clear_start()     #reset game state(position of tiger and state of player)
            elif action == open_right:
                if self.tiger == right:
                    self.reward -= 100
                else:
                    self.reward += 30
                tmp_reward = self.reward
                tmp_observation = self.observation
                self.clear_start()
            else:
                self.reward -= 10
        if tmp_reward < 0:
            tmp_reward = 0
        return tmp_observation, tmp_reward
    # end def
    def clear_start(self):
        print("Game Over! Starting New Game...")
        self.reward = 128
        self.observation = void
        self.state = sitting
        self.tiger = left if random.randint(0,1) == 1 else right
        print(f"Tiger be set at the :{self.tiger}")
        
    def print(self):
        print("==" * 20)
        print(f"Reward :{self.reward-100}")
        print(f"State :{tiger_state_enum[self.state]}")
        print(f"Actions :{tiger_action_enum[self.action]}")
        print(f"Tiger is at {tiger_observation_enum[self.tiger]}")
        print(f"Observation : {tiger_observation_enum[self.observation]}")
        print(self)