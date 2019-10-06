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

# Insert the package's parent directory into the system search path, so that this package can be
# imported when the aixi.py script is run directly from a release archive.
PROJECT_ROOT = os.path.realpath(os.path.join(os.pardir, os.pardir))
sys.path.insert(0, PROJECT_ROOT)

from pyaixi import environment, util

# extended tiger has 4 actions in total encoded in 2 bits
tiger_action_enum = util.enum('stand','listen','open_left_door','open_right_door')
# Oberservation encoded into 2 bits
tiger_observation_enum = util.enum('left','right','void') # Observation enum may need to be modified to satisfy 3 bits
# Reward is encoded into 8 bits range from 0 to 130
# 0(-100) reward is given by choosing the worst action: open the door with tiger hiding behind
# 90(-10) reward is given by choosing an 'invalid' action: e.g. stand while standing
# 99(-1)  reward is given by choosing an 'valid' action: e.g. sitting -> stand
# 130(30) reward is given by choosing the best action: open the door with gold behind
# 0, and 90 reward are the cases agent wants to avoid
tiger_reward_enum = util.enum(penalty = 90, eaten = 0, gold = 130, normal = 99)
# envrionment state: whethere the player is sitting or standing
tiger_state_enum = util.enum('sitting', 'standing')

# for coding convenience

sitting = tiger_state_enum.sitting
standing = tiger_state_enum.standing
stand = tiger_action_enum.stand
listen = tiger_action_enum.listen
open_left = tiger_action_enum.open_left_door
open_right = tiger_action_enum.open_right_door

left = tiger_observation_enum.left
right = tiger_observation_enum.right
void = tiger_observation_enum.void

penalty = tiger_reward_enum.penalty
normal = tiger_reward_enum.normal
eaten = tiger_reward_enum.eaten
gold = tiger_reward_enum.gold


class ExtendedTiger(environment.Environment):
    """ A tiger and a pot of gold are hidden behind one of two doors. Initially 
        the agent begins sitting down on a chair. The agent has a choice of one
        of four actions: stand, listen, open left door, open right door. While
        sitting, the actions are valid to environment are "listen" and "stand".
        Each action would resulting in a reward of -1 while any other "invalid"
        actions would result in a penalty reward of -10. While standing, the
        actions valid to environment are "open left door" and "open right door"
        and rewards are same as state = sitting. Our goal is to let agent open
        the door with gold behind in best sequence of actions(highest reward).
        The game will end and restart by open any door.
        
        Domain characteristics:
            
        - environment: "exxtended_tiger"
        - maximum action: 3 (2 bit)
        - maximum observation: 3 (2 bit)
        - maximum reward: 130 (8 bit)
        
        Configuration options:
        - ''
    """
    # Instance attributes.

    # Set the default probability for listening(agent has 0.85 chance to predict the correct location by performing listen)
    default_probability = 0.85

    # Instance methods.

    def __init__(self, options = {}):
        """ Construct the ExtendedTiger environment from the given options.

             - `options` is a dictionary of named options and their values.

            The following options in `options` are optional:
            
             - `extended-tiger-p`: the probability that the agent will find the tiger. (Defaults to 0.85)
        """

        # Set up the base environment.
        environment.Environment.__init__(self, options = options)

        # Defines the acceptable action values.
        self.valid_actions = list(tiger_action_enum.keys())

        # Defines the acceptable observation values.
        self.valid_observations = list(tiger_observation_enum.keys())
        
        self.valid_rewards = list(tiger_reward_enum.keys())
        # Set an initial percept.
        self.reward = 0
        self.tmp_reward = 0 # restore temprory reward to display sum of reward of a single game run
        self.state = sitting # represent the state of agent(sitting/standing) initially set to be sitting
        self.tiger = left if random.randint(0,1) == 1 else right # set initial position of tiger
        self.observation = void
    # end def

    def perform_action(self, action):
        """ Receives the agent's action and calculates the new environment percept.
        """

        assert self.is_valid_action(action)
        # Save the action.
        self.action = action
        # Conditions while sitting
        if self.state == sitting:
            if action == stand:
                self.reward = normal# reward by performing valid actions
                self.state = standing# change state to standing 
            elif action == listen:
                self.reward = normal# reward by performing valid actions
                if (random.random() < self.default_probability): # give chance to correct predicting tiger location
                    self.observation = self.tiger
                else:
                    # while the chance does not happen, give a misleading info
                    if self.tiger == left:
                        self.observation = right
                    else:
                        self.observation = left
            else:
                # reward by performing invalid action
                self.reward = penalty
        # Conditions while standing
        else:
            if action == open_left: # Open left door
                if self.tiger == left:
                    self.reward = eaten # if tiger is behind left door you got eaten!
                else:
                    self.reward = gold # otherwise, You find the GOLD!
                self.clear_start() # initiate the game 
            elif action == open_right: 
                if self.tiger == right: # Open right door
                    self.reward = eaten
                else:
                    self.reward = gold
#                print("BUG 1")
#                self.state = sitting
                self.clear_start()
            else:
                self.reward = penalty
        self.tmp_reward += (self.reward - 100)
#        print("PASSING")
        return (self.observation, self.reward)
    # end def
    def clear_start(self):
#        print("Game Over! Starting New Game...")
        self.tmp_reward = 0
        self.state = sitting
        self.tiger = left if random.randint(0,1) == 1 else right
#        print(f"Tiger be set at the :{self.tiger}")
        
    def print(self):
        print("==" * 20)
        print(f"Total Reward:{self.tmp_reward+self.reward-100}")# Not able to show the last reward
        
        print(f"Action Reward :{self.reward-100}")
        print(f"State :{tiger_state_enum[self.state]}")
        print(f"Actions :{tiger_action_enum[self.action]}")
        print(f"Tiger is at {tiger_observation_enum[self.tiger]}")
        print(f"Observation : {tiger_observation_enum[self.observation]}")
        print(self)
