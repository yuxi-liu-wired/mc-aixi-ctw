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

# Defines an enumeration to represent agent action: bet on current observation or pass.
kp_action_enum = util.enum('pas', 'bet')

# Defines an enumeration to represent agent observation: two type of observations
# - encode Agent's current card as observation
# - encode Opponent's choice of "Pass" or "Bet" as observation
kp_card_observation_enum = util.enum(j=1, q=2, k=3)
kp_opponent_observation_enum = util.enum(opBet=4, opPass=8)

# Win a bet will gain 2 chips thus the best reward, Loss a bet will lose 2 chips thus the worst reward.
kp_bet_reward_enum = util.enum(betWin = 4, betLoss = 0) 
# Win by pass will gain 1 chip, Loss by pass will lose 1 chips
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
    """ Kuhn poker is an extremely simplified form of poker as a simple model 
        zero-sum two-player imperfect-information game. In Kuhn poker, the deck
        includes only three playing cards, for example a King, Queen, and Jack.
        One card is dealt to each player, which may place bets similarly to a 
        standard poker. If both players bet or both players pass, the player
        with the higher card wins, otherwise, the betting player wins.
        (reference: (wikipedia)https://en.wikipedia.org/wiki/Kuhn_poker)
        
        While game start, agent will firstly pick out one card from deck and
        the Opponent(environment) will then choose from the rest two cards.
        At each game, the opponent will always be the first to make actions.
        
        Actions: Two actions, "pass" or "bet", are available to each player. 
        When "bet" is chosen, the player is required to put extra chip(reward)
        to game. If both players choose the same actions at the end, a
        show down will occur while the player with higher card will instantly 
        win the round("K" beats "Q" beats "J"). After cards were drawn, the 
        opponent will firstly choose to "bet" or "pass". If "pass" is chosen by
        opponent as the first action and agent subsequently chose to "bet" then
        the opponent will have a secondary chance to change his mind. In the
        end, if one chooses to pass while the other wants to bet, then the one
        who's betting will instantly win the game("Pass Win")
        
        The reward of the game is equal to chips put into the game(2-4) while
        winner gains amount he put into the game(e.g. 1 or 2) and loser lost 
        the same amount that the other player wins.
        
        Game clear and restart: after a round is finished(showdown or "Pass win
        "), all chips from previous game will be cleared, rewards will be 
        calculated and players will be reassigned with new cards and starting 
        putting chips again.
        
        Domain characteristics:

        - environment: "kuhn_poker"
        - maximum action: 2 (1 bit)
        - maximum observation: 11 (4 bit)
        - maximum reward: 4 (3 bit)
    """

    # Instance attributes.

    # Set the default probability for the opponent wants to bet on Q.
    default_probability = 0.7

    # Instance methods.

    def __init__(self, options = {}):
        """ Construct the KuhnPoker environment from the given options.

             - `options` is a dictionary of named options and their values.

            The following options in `options` are optional:
            
             - `kuhn-poker-p`: the probability that the opponent will bet on Q. (Defaults to 0.7.)
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
            self.op_action = opPass # Opponent always pass on J
        elif self.op_card == q:
            if random.random() < self.default_probability: # Opponent has probability bet on Q
                self.op_action = opPass
            else:
                self.op_action = opBet 
        else:
            self.op_action = opBet # Opponent always bet on K
        
        self.observation = self.calculate_observation()
    # end def
    
    # Function to calcute the correct observation that needs to be passed to agent
    def calculate_observation(self):
        """ Calculate the KuhnPoker observation from the agent's card and opponent's action.
            The opponent's actions and agent's card are uniquely decoded but to agent,
            it can receive both observations when it performs action. Thus, these two
            observation needed to be add up.
            
            Observation Dictionary:
            
            {1: agent has card "Jack", 2: agent has card "Queen", 3: agent has card "King",
            4: Opponent chose to "bet", 8: Opponent chose to "pass", 5: agent has card "J"
            and Opponent bet, 6: agent has card "Q" and Opponent bet, 7: agent has card
            "K" and Opponent bet, 9: agent_card "J" and Opponent passed, 10: agent_card "Q"
            and Opponent passed, 11: agent_card "K" and Opponent passed
        """
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
        observation = self.observation # restore
        if self.action == pas and self.op_action == opPass: # Condition: Both players passed
            if (self.op_card == j) or (self.op_card == q and self.agent_card == k): # Higher card wins
                self.reward = pasWin # Agent win 1 chip
            else:
                self.reward = pasLoss # Agent lost 1 chip
            self.clear_start() # Clear and start new round
            return observation, self.reward
        if self.action == bet and self.op_action == opBet: # Condition: Both players bet
            if (self.op_card == j) or (self.op_card == q and self.agent_card == k):
                self.reward = betWin # Agent win 2 chip
            else:
                self.reward = betLoss # Agent lost 2 chip
            self.clear_start()
            return observation, self.reward
        if self.action == bet and self.op_action == opPass: # Condition: Opponent's first action is pass and agent bet
            if (self.op_card == q and random.random() < self.default_probability) or self.op_card == k: # give a probability to bet on Q or always bet on K
                self.op_action = opBet
                #print("Opponent changed his mind and choose to bet")
                self.observation = self.calculate_observation() # give new observation
                observation = self.observation
                if (self.op_card == j) or (self.op_card == q and self.agent_card == k):
                    self.reward = betWin # Agent win bet
                else:
                    self.reward = betLoss # Agent loss bet
                self.clear_start()
                return observation, self.reward
            else:
                self.op_action = opPass
                self.reward = pasWin
                self.clear_start()
                return observation, self.reward
        else:
            self.reward = pasLoss
            self.clear_start()
        return observation, self.reward

    # end def
    def clear_start(self): # Start a new round, reset the players' cards and give new observation
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
    def running(self):
        while not self.is_finished:
                
            print(self)
            print("==" * 20)
            print(f"Reward of last game: {self.reward-2}")
            print(f"Your card is:{kp_card_observation_enum[self.agent_card]}")
            print(f"Opponent choose to : {kp_opponent_observation_enum[self.op_action]}")
            print(f"Opponent has card : {kp_card_observation_enum[self.op_card]}")
            
            action = input("Action is :  ")
            
            if action == "bet":
            
                action = 0
                
            elif action == "pass":
            
                action  = 1
                    
            self.perform_action(action)
            
            
        print("**"*20)
        print('{:^40}'.format("Game Over"))
        print("**"*20)    

