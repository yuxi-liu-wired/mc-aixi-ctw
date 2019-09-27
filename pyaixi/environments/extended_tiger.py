#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 27 09:00:01 2019

@author: jiayanliu
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
tiger_observation_enum = util.enum('left','right')
tiger_state_enum = util.enum('sitting', 'standing')

sitting = tiger_state_enum.sitting
standing = tiger_state_enum.standing
stand = tiger_action_enum.stand
listen = tiger_action_enum.listen
open_left = tiger_action_enum.open_left_door
open_right = tiger_action_enum.open_right_door
left = tiger_observation_enum.left
right = tiger_observation_enum.right

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
        self.maxium_reward = 30
        environment.Environment.__init__(self, options = options)

        # Defines the acceptable action values.
        self.valid_actions = list(tiger_action_enum.keys())

        # Defines the acceptable observation values.
        self.valid_observations = list(tiger_observation_enum.keys())
        
        self.valid_rewards = range(self.maxium_reward)
        # Set an initial percept.
        self.reward = 0
        self.is_finished = False
        self.state = sitting
        self.observation = left if random.randint(0,1) == 1 else right
        self.tiger = left if random.randint(0,1) == 1 else right
    # end def

    def perform_action(self, action):
        """ Receives the agent's action and calculates the new environment percept.
        """

        assert self.is_valid_action(action)
        observation = self.observation
        # Save the action.
        self.action = action
        if self.state == sitting:
            if action == stand:
                self.reward = -1
                self.state = standing
            elif action == listen:
                self.reward = -1
                if (random.random() < self.default_probability):
                    observation = self.tiger
                else:
                    if self.tiger == left:
                        observation = right
                    else:
                        observation = left
            else:
                self.reward = -10
        else:
            if action == open_left:
                if self.tiger == left:
                    self.reward = -100
                else:
                    self.reward = 30
            elif action == open_right:
                if self.tiger == right:
                    self.reward = -100
                else:
                    self.reward = 30
            else:
                self.reward = -10
        self.reward = max(self.reward,0)
        return (observation, self.reward)
    # end def
    def clear_start(self):
        self.reward = 0
        self.state = sitting
        self.tiger = left if random.randint(0,1) == 1 else right
        
    def print(self):
        print("==" * 20)
        print(f"Reward :{self.reward}")
        print(f"Tiger is at {tiger_observation_enum[self.tiger]}")
        print(f"Observation : {tiger_observation_enum[self.observation]}")
        print(self)