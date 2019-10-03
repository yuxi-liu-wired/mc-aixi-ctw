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

from pyaixi import environment, util

description = 'extended_tiger.txt'

tiger_action_enum = util.enum('stand','listen','open_left_door','open_right_door')
print(tiger_action_enum)
tiger_observation_enum = util.enum('left','right','void')
tiger_reward_enum = util.enum(penalty = 90, eaten = 0, gold = 130, normal = 99)
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

penalty = tiger_reward_enum.penalty
normal = tiger_reward_enum.normal
eaten = tiger_reward_enum.eaten
gold = tiger_reward_enum.gold


class ExtendedTiger(environment.Environment):
    """ A biased coin is flipped and the agent is tasked with predicting how it
        will land. The agent receives a reward of `rWin` for a correct
        prediction and `rLoss` for an incorrect prediction. The observation
        specifies which side the coin landed on (`oTails` or `oHeads`).
        The action corresponds to the agent's prediction for the
        next coin flip (`aTails` or `aHeads`).

        Domain characteristics:

        - environment: "coin_flip"
        - maximum action: 1 (1 bit)
        - maximum observation: 1 (1 bit)
        - maximum reward: 1 (1 bit)

        Configuration options:
        - `coin-flip-p`: the probability the coin lands on heads
                         (`oHeads`). Must be a number between 0 and 1 inclusive.
                         Default value is `default_probability`.
                         (Optional.)
    """

    # Instance attributes.

    # Set the default probability for the biased coin, when none is supplied from the options.
    default_probability = 0.85

    # Instance methods.

    def __init__(self, options = {}):
        """ Construct the CoinFlip environment from the given options.

             - `options` is a dictionary of named options and their values.

            The following options in `options` are optional:
            
             - `coin-flip-p`: the probability that the coin will land on heads. (Defaults to 0.7.)
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
        self.tmp_reward = 0
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
        if self.state == sitting:
            if action == stand:
                self.reward = normal
                self.state = standing
            elif action == listen:
                self.reward = normal
                if (random.random() < self.default_probability):
                    self.observation = self.tiger
                else:
                    if self.tiger == left:
                        self.observation = right
                    else:
                        self.observation = left
            else:
                self.reward = penalty
        else:
            if action == open_left:
                if self.tiger == left:
                    self.reward = eaten
                else:
                    self.reward = gold
#                print("bug 2")
#                self.state = sitting
                self.clear_start()
            elif action == open_right:
                if self.tiger == right:
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
