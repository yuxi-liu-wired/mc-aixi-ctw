#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 28 00:51:07 2019

@author: jiayanliu,Wenxi Wu
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import random
import sys

# Insert the package's parent directory into the system search path, so that this package can be
# imported when the aixi.py script is run directly from a release archive.
PROJECT_ROOT = os.path.realpath(os.path.join(os.pardir, os.pardir))
sys.path.insert(0, PROJECT_ROOT)

from pyaixi import environment, util

# Defines an enumeration to represent agent action: a prediction of whether the coin will land on
# heads or tails.
kp_action_enum = util.enum('pas', 'bet')

# Defines an enumeration to represent agent observation: whether the coin landed on heads or tails.
kp_card_observation_enum = util.enum(j=0, q=1, k=2)
kp_opponent_observation_enum = util.enum(opBet=3, opPass=4)

# Defines an enumeration to represent agent reward: whether the gaent predicted correctly.
kp_bet_reward_enum = util.enum(betWin = 4, betLoss = 0)
kp_pass_reward_enum = util.enum(pasWin = 3, pasLoss = 1)

# Defines some shorthand notation for ease of reference.
pas = kp_action_enum.pas
bet = kp_action_enum.bet

j = kp_card_observation_enum.j
q = kp_card_observation_enum.q
k = kp_card_observation_enum.k
opBet = kp_opponent_observation_enum.opBet
opPass = kp_opponent_observation_enum.opPass

betWin = kp_bet_reward_enum.betWin
betLoss = kp_bet_reward_enum.betLoss
pasWin = kp_pass_reward_enum.pasWin
pasLoss = kp_pass_reward_enum.pasLoss

card_list = [j,q,k]

class KuhnPoker(environment.Environment):
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
    default_probability = 0.7

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
        self.valid_actions = list(kp_action_enum.keys())

        # Defines the acceptable observation values.
        self.valid_observations = list(kp_card_observation_enum.keys())+list(kp_opponent_observation_enum.keys())

        # Defines the acceptable reward values.
        self.valid_rewards = list(kp_bet_reward_enum.keys())+list(kp_pass_reward_enum.keys())


        # Set an initial percept.
        self.reward = 0
        self.agent_card = util.choice(card_list)
        self.op_card = util.choice([x for x in card_list if x != self.agent_card])
        if self.op_card == j:
            self.op_action = opPass
        elif self.op_card == q:
            if random.random() < self.default_probability:
                self.op_action = opPass
            else:
                self.op_action = opBet
        else:
            self.op_action = opBet
        
        #Question: does opponent always go first?
        self.observation = self.calculate_observation()
    # end def
    def calculate_observation(self):
        if self.op_action == opPass:
            observation = opPass
        else:
            observation = opBet
        return observation + self.agent_card
    def perform_action(self, action):
        """ Receives the agent's action and calculates the new environment percept.
        """

        assert self.is_valid_action(action)

        # Save the action.
        self.action = action
        if self.action == pas and self.op_action == opPass:
            if (self.op_card == j) or (self.op_card == q and self.agent_card == k):
                self.reward = pasWin
            else:
                self.reward = pasLoss
            self.clear_start()
            return self.observation, self.reward
        if self.action == bet and self.op_action == opBet:
            if (self.op_card == j) or (self.op_card == q and self.agent_card == k):
                self.reward = betWin
            else:
                self.reward = betLoss
            self.clear_start()
            return self.observation, self.reward
        if self.action == bet and self.op_action == opPass:
            if (self.op_card == q and random.random() < self.default_probability) or self.op_card == k:
                self.op_action = opBet
                self.observation = self.calculate_observation()
            else:
                self.op_action = opPass
                self.reward = pasWin
                self.clear_start()
                return self.observation, self.reward
        else:
            self.reward = pasLoss
#        elif self.action == pas and self.op_action == bet:
#            self.reward = pasLoss
#            return self.observation, self.reward
#        elif self.action == bet and self.op_action == pas:
#            self.reward = pasWin
            self.clear_start()
        return self.observation, self.reward

    # end def
    def clear_start(self):
#        print("Previous finish, Restarting Game")
        self.agent_card = util.choice(card_list)
        self.op_card = util.choice([x for x in card_list if x != self.agent_card])
        if self.op_card == j:
            self.op_action = opPass
        elif self.op_card == q:
            if random.random() < self.default_probability:
                self.op_action = opPass
            else:
                self.op_action = opBet
        else:
            self.op_action = opBet
        
        #Question: does opponent always go first?
        self.observation = self.calculate_observation()
    def print(self):
        """ Returns a string indicating the status of the environment.
        """

        print("==" * 20)
        print(f"Reward :{self.reward-2}")
        print(f"Agent Actions :{kp_action_enum[self.action]}")
        print(f"Opponent Actions :{kp_opponent_observation_enum[self.op_action]}")
        print(f"Agent has card : {kp_card_observation_enum[self.agent_card]}")
        print(f"Opponent has card : {kp_card_observation_enum[self.op_card]}")
        print(self)
    # end def
# end class

