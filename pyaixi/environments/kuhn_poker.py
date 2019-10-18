#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 28 00:51:07 2019

@author: Jiayan Liu, Wenxi Wu.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from pyaixi import environment, util
import os
import random
import sys

# Insert the package's parent directory into the system search path, so that this package can be
# imported when the aixi.py script is run directly from a release archive.
PROJECT_ROOT = os.path.realpath(os.path.join(os.pardir, os.pardir))
sys.path.insert(0, PROJECT_ROOT)


# Defines an enumeration to represent agent action: bet on current observation or pass.
kp_action_enum = util.enum('agent_pass', 'agent_bet')

# Defines an enumeration to represent agent observation.
# The agent observes both its own card and the opponent's action.
kp_card_observation_enum = util.enum(j = 0, q = 1, k = 2)
kp_opponent_observation_enum = util.enum(op_bet = 0, op_pass = 3)
# Observation codes:
# 0: agent has J, Opponent bet,
# 1: agent has Q, Opponent bet,
# 2: agent has K, Opponent bet,
# 3: agent has J, Opponent passed,
# 4: agent has Q, Opponent passed,
# 5: agent has K, Opponent passed.

# Reward is (final chip count) - (initial chip count).
kp_bet_reward_enum = util.enum(fourChips = 4, threeChips = 3,
                               oneChip = 1, zeroChips = 0)

# Defines some shorthand notation for ease of reference.
agent_pass = kp_action_enum.agent_pass
agent_bet = kp_action_enum.agent_bet

j = kp_card_observation_enum.j
q = kp_card_observation_enum.q
k = kp_card_observation_enum.k
card_list = [j, q, k]

op_bet = kp_opponent_observation_enum.op_bet
op_pass = kp_opponent_observation_enum.op_pass

fourChips = kp_bet_reward_enum.fourChips
threeChips = kp_bet_reward_enum.threeChips
oneChip = kp_bet_reward_enum.oneChip
zeroChips = kp_bet_reward_enum.zeroChips


class KuhnPoker(environment.Environment):
    """ Kuhn poker is an extremely simplified form of poker. It is a zero-sum
        two-player imperfect-information game that is analytically solved.

        The deck contains 3 cards: King, Queen, and Jack, ordered by K > Q > J
        in a showdown. Since there are no duplicates, draws are impossible.

        There are 2 actions: "agent_pass" and "agent_bet".
        - agent_pass: player puts no extra chips to the pot.
        - agent_bet: player puts an extra chip to the pot.

        When the game starts, the agent and the opponent both have 1 chip,
        and 1 card from the deck. There are 2 chips in the pot.

        Opponent acts first.

        If opponent passes, then
            If agent passes, there is a showdown for the pot of 2.
                If agent wins, then agent wins the pot of 2, ending up with 3 chips (threeChips).
                If agent loses, then agent loses the pot of 2, ending up with 1 chip (oneChip).
            If agent bets, then
                If opponent passes, then agent wins the pot of 3 (threeChips).
                If opponent bets, there is a showdown for the pot of 4.
                    If agent wins, then agent wins the pot of 4, ending up with 4 chips (fourChips).
                    If agent loses, then agent loses the pot of 4, ending up with 0 chips (zeroChips).
        If opponent bets, then
            If agent passes, then agent loses the pot of 3, ending up with 1 chip (oneChip).
            If agent bets, there is a showdown for the pot of 4.
                If agent wins, then agent wins the pot of 4, ending up with 4 chips (fourChips).
                If agent loses, then agent loses the pot of 4, ending up with 0 chips (zeroChips).

        The opponent plays the Nash equilibrium strategy:
            In turn one, always pass.
            If agent passes, then showdown, and there won't be a turn two.
            Else, agent bets, and
                If opponent has J, pass.
                If opponent has Q, bet with probability 1/3.
                If opponent has K, bet.

        An optimal agent should have average reward 1/18 per round.
        That translates to average reward 2.0555.

        Domain characteristics:

        - environment: "kuhn_poker"
        - maximum action: 2 (1 bit)
        - maximum observation: 5 (3 bits)
        - maximum reward: 4 (3 bits)
    """

    # Instance attributes.

    # The default probability for the opponent to bet on Q in round 2.
    default_probability = 1/3


    # Instance methods.

    def __init__(self, options={}):
        """ Construct the KuhnPoker environment from the given options.

             - `options` is a dictionary of named options and their values.

            The following options in `options` are optional:

             - `kuhn-poker-p`: the probability that the opponent will bet on Q. (Defaults to 1/3.)
        """

        # Set up the base environment.
        environment.Environment.__init__(self, options=options)

        # Defines the acceptable action values.
        self.valid_actions = list(kp_action_enum.keys())

        # Defines the acceptable observation values.
        self.valid_observations = [0, 1, 2, 3, 4, 5]

        # Defines the acceptable reward values.
        self.valid_rewards = list(kp_bet_reward_enum.keys())

        self.reward = 0
        self.restart()
    # end def

    def restart(self):
        """ Start a new round, reset the players' cards, give new observation.
        """
        # Initialize game state.
        self.agent_card, self.op_card = random.sample(card_list, 2) # Deal cards.
        self.agent_wins_showdown = self.agent_card > self.op_card
        self.op_action_1 = op_pass # Opponent always passes first turn.

        # Initialize observation.
        self.observation = self.op_action_1 + self.agent_card
    # end def

    def perform_action(self, action):
        """ Receives the agent's action, calculates the opponent's response
            (if needed), calculates the game outcome, then starts a new game, and
            returns the new game's observation and the old game's reward.
        """

        assert self.is_valid_action(action)
        self.action = action

        if self.action == agent_pass and self.op_action_1 == op_pass:  # Both players passed.
            if self.agent_wins_showdown:
                self.reward = threeChips
            else:
                self.reward = oneChip

        elif self.action == agent_bet and self.op_action_1 == op_bet:  # Both players betted
            if self.agent_wins_showdown:
                self.reward = fourChips
            else:
                self.reward = zeroChips

        elif self.action == agent_bet and self.op_action_1 == op_pass: # Opponent passed, agent betted.
            if (self.op_card == q and random.random() < self.default_probability) or self.op_card == k:
                self.op_action_2 = op_bet # Opponent bets again.
            else:
                self.op_action_2 = op_pass # Opponent folds.

            if self.op_action_2 == op_bet: # Opponent bets again.
                if self.agent_wins_showdown:
                    self.reward = fourChips
                else:
                    self.reward = zeroChips
            else: # Opponent folds.
                self.reward = threeChips

        else: # Opponent betted, agent passed.
            self.reward = oneChip
        # end if

        # Start a new game and return the observation on the new game.
        self.restart()
        return self.observation, self.reward
    # end def

#    def print(self):
#        """ Returns a string indicating the status of the environment.
#        """
#        print("==" * 20)
#        print(f"Reward :{self.reward-2}")
#        print(f"Agent Actions :{kp_action_enum[self.action]}")
#        print(
#            f"Opponent Actions :{kp_opponent_observation_enum[self.op_action_1]}")
#        print(f"Agent has card : {kp_card_observation_enum[self.agent_card]}")
#        print(f"Opponent has card : {kp_card_observation_enum[self.op_card]}")
#        print(self)
#    # end def
#
#    
#    def running(self):
#        while not self.is_finished:
#
#            print(self)
#            print("==" * 20)
#            print(f"Reward of last game: {self.reward-2}")
#            print(f"Your card is:{kp_card_observation_enum[self.agent_card]}")
#            print(
#                f"Opponent choose to : {kp_opponent_observation_enum[self.op_action_1]}")
#            print(
#                f"Opponent has card : {kp_card_observation_enum[self.op_card]}")
#
#            action = input("Action is :  ")
#
#            if action == "bet":
#
#                action = 0
#
#            elif action == "pass":
#
#                action = 1
#
#            self.perform_action(action)
#
#        print("**" * 20)
#        print('{:^40}'.format("Game Over"))
#        print("**" * 20)
