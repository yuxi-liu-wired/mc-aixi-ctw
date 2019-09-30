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
import itertools

# Insert the package's parent directory into the system search path, so that this package can be
# imported when the aixi.py script is run directly from a release archive.
PROJECT_ROOT = os.path.realpath(os.path.join(os.pardir, os.pardir))
sys.path.insert(0, PROJECT_ROOT)

from pyaixi import environment, util


kp_action_enum = util.enum('pas', 'bet')

kp_card_observation_enum = util.enum('jack', 'queen', 'king')
kp_opponent_observation_enum = util.enum('bet', 'pas')
valid_observations_enum = util.enum('jb','jp','qb','qp','kb','kp')

# Defines some shorthand notation for ease of reference.
pas = kp_action_enum.pas
bet = kp_action_enum.bet

jack = kp_card_observation_enum.jack
queen = kp_card_observation_enum.queen
king = kp_card_observation_enum.king
card_list = [jack,queen,king]

alpha = random.uniform(0, 0.33)


class KuhnPoker(environment.Environment):

    # Instance methods.

    def __init__(self, options = {}):

        # Set up the base environment.
        environment.Environment.__init__(self, options = options)

        # Defines the acceptable action values.
        self.valid_actions = list(kp_action_enum.keys())

        # Defines the acceptable observation values.
        self.valid_observations = list(valid_observations_enum.keys())

        # Defines the acceptable reward values.
        self.valid_rewards = range(2**3)
        # Set an initial percept.
        self.initGame()
    # end def

    def perform_action(self, action):
        """ Receives the agent's action and calculates the new environment percept.
        """

        assert self.is_valid_action(action)
        self.agent_bet = action
                                                                               
        if action == bet:                                                       
            self.sec_player_payoff += 1                                         
            if self.op_bet == bet:                                              
                self.showdown()                                                                 
            elif self.op_bet == pas:                                            
                if self.op_card == jack:
                    self.op_bet = pas
                    self.reward += self.fst_player_payoff + self.sec_player_payoff
                elif self.op_card == queen:
                    self.op_bet = bet if random.random() < alpha + 0.33 else pas
                    if self.op_bet == bet:
                        self.fst_player_payoff += 1
                        self.showdown()
                    elif self.op_bet == pas:
                        self.reward += self.fst_player_payoff + self.sec_player_payoff
                elif self.op_card == king:
                    self.op_bet = bet
                    self.fst_player_payoff += 1
                    self.showdown()
        elif action == pas:
            if self.op_bet == bet:
                self.reward -= self.sec_player_payoff
            elif self.op_bet == pas:
                self.showdown()  
        # Save the action.
        tmp_observation = self.observation
        tmp_reward = self.reward
        self.initGame()
        return tmp_observation, tmp_reward

    # end def

    #showdown process return true if opponent win, false if agent win
    def showdown(self):
        if self.convertCardToInt(self.op_card) > self.convertCardToInt(self.agent_card):
            self.reward -= self.sec_player_payoff
        else:
            self.reward += self.fst_player_payoff + self.sec_player_payoff


    def calculateObservation(self, agent_card, opponent):
        if agent_card == jack:
            if opponent == pas:
                self.observation = valid_observations_enum.jp
            elif opponent == bet:
                self.observation = valid_observations_enum.jb
        elif agent_card == queen:
            if opponent == pas:
                self.observation = valid_observations_enum.qp
            elif opponent == bet:
                self.observation = valid_observations_enum.qb
        elif agent_card == king:
            if opponent == pas:
                self.observation = valid_observations_enum.kp
            elif opponent == bet:
                self.observation = valid_observations_enum.kb

    def convertCardToInt(self, card):
        if card == jack:
            return 1
        if card == queen:
            return 2
        if card == king:
            return 3

    def initGame(self):
        self.reward = 3

        self.agent_card = util.choice(card_list)
        self.agent_bet = None

        self.op_card = util.choice([x for x in card_list if x != self.agent_card])
        self.op_bet = None

        self.fst_player_payoff = 1
        self.sec_player_payoff = 1

        if self.op_card == jack:
            self.op_bet = bet if random.random() < alpha else pas
        elif self.op_card == queen:
            self.op_bet = pas
        elif self.op_card == king:
            self.op_bet = bet if random.random() <  3*alpha else pas

        if self.op_bet == bet:
            self.fst_player_payoff += 1
        self.calculateObservation(self.agent_card, self.op_bet)



    def print(self):
        """ Returns a string indicating the status of the environment.
        """
        # print("==" * 20)
        # print(f"Reward :{self.reward}")
        # print(f"Agent Actions :{kp_action_enum[self.action]}")
        # print(f"Opponent Actions :{kp_action_enum[self.op_action]}")
        # print(f"Agent has card : {kp_card_observation_enum[self.agent_card]}")
        # print(f"Opponent has card : {kp_card_observation_enum[self.op_card]}")
        # print(self)
    # end def
# end class
