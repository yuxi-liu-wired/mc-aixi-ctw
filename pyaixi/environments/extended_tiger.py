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


# 4 actions, encoded in 2 bits.
tiger_action_enum = util.enum('stand','listen','open_left_door','open_right_door')

# 3 Oberservations, encoded in 2 bits.
# 'left': the tiger is behind the left door.
# 'right': the tiger is behind the right door.
# 'void': the agent tried to listen while standing, and thus heard nothing.
tiger_observation_enum = util.enum('left','right','void')

# Reward ranges from 0 to 130, encoded in 8 bits.
# 0(-100) reward is given by choosing the worst action: open the door with tiger hiding behind.
# 90(-10) reward is given by choosing an 'invalid' action: e.g. stand while standing.
# 99(-1)  reward is given by choosing an 'valid' action: e.g. stand sitting.
# 130(30) reward is given by choosing the best action: open the door with gold behind.
tiger_reward_enum = util.enum(penalty = 90, eaten = 0, gold = 130, normal = 99)

# 2 states, encoded in 1 bit.
tiger_state_enum = util.enum('sitting', 'standing')

# Defines some shorthand notation for ease of reference.
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
        of four actions: stand, listen, open left door, open right door.

        While sitting, the valid actions are "listen" and "stand". Each valid
        action results in a reward of -1, invalid actions -10.

        While standing, the valid actions are "open left door" and "open right
        door". Opening the door to the gold results in reward 30. Opening the
        door to the tiger results in reward -100.

        The game will end and restart by opening any door.

        Domain characteristics:

        - environment: "extended_tiger"
        - maximum action: 3 (2 bits)
        - maximum observation: 3 (2 bits)
        - maximum reward: 130 (8 bits)
    """
    # Instance attributes.

    # By default, agent has 0.85 chance to hear the tiger.
    default_probability = 0.85


    # Instance methods.

    def __init__(self, options = {}):
        """ Construct the ExtendedTiger environment from the given options.

             - `options`: a dictionary of named options and their values.

            The following options in `options` are optional:

             - `extended-tiger-p`: the probability that the agent will hear the tiger. (Defaults to 0.85)
        """

        # Set up the base environment.
        environment.Environment.__init__(self, options = options)

        # Defines the acceptable action values.
        self.valid_actions = list(tiger_action_enum.keys())

        # Defines the acceptable observation values.
        self.valid_observations = list(tiger_observation_enum.keys())

        # Defines the acceptable reward values.
        self.valid_rewards = list(tiger_reward_enum.keys())

#        self.total_reward = 0 # restore temprory reward to display sum of reward of a single game run
        self.restart()
        self.reward = 0
    # end def

    def perform_action(self, action):
        """ Receives the agent's action and calculates the new environment percept.
        """

        assert self.is_valid_action(action)
        self.action = action

        if self.state == sitting:
            if action == stand: # Valid action reward.
                self.reward = normal
                self.state = standing
            elif action == listen:
                self.reward = normal # Valid action reward.
                # Randomly decide if the agent heard the tiger correctly.
                if (random.random() < self.default_probability):
                    # Heard it correctly.
                    self.observation = self.tiger
                else: # Heard it incorrectly.
                    if self.tiger == left:
                        self.observation = right
                    else:
                        self.observation = left
            else: # Invalid action reward.
                self.reward = penalty
            # end if
        else:
            assert self.state == standing
            if action == open_left:
                if self.tiger == left:
                    self.reward = eaten
                else:
                    self.reward = gold
                self.restart()
            elif action == open_right:
                if self.tiger == right:
                    self.reward = eaten
                else:
                    self.reward = gold
                self.restart()
            else: # Invalid action reward.
                self.reward = penalty
            # end if
        # end if

#        self.total_reward += (self.reward - 100)
        return (self.observation, self.reward)
    # end def

    def restart(self):
        """ Restarts the game.
        """
        self.state = sitting # Agent starts sitting.
        self.observation = void # Agent starts hearing nothing.
        # Randomly initialize tiger location.
        self.tiger = left if random.randint(0,1) == 1 else right

#    def print(self):
#        """ Returns a string indicating the status of the environment.
#        """
#
#        print("=" * 40)
#        print(f"Total Reward: {self.total_reward}")
#        # Not able to show the last reward
#
#        print(f"Action Reward: {self.reward-100}")
#        print(f"State: {tiger_state_enum[self.state]}")
#        print(f"Actions: {tiger_action_enum[self.action]}")
#        print(f"Tiger is at {tiger_observation_enum[self.tiger]}")
#        print(f"Observation: {tiger_observation_enum[self.observation]}")
#        print(self)
