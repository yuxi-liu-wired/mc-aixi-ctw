#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Defines a class to implement a Monte Carlo search tree.

Implementation based on:
Cameron B Browne et al. “A Survey of Monte Carlo Tree Search Methods.”, 2012
Joel Veness et al. “A Monte-Carlo Aixi Approximation.”, 2011
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import math
import random
import sys

# Insert the package's parent directory into the system search path, so that this package can be
# imported when the aixi.py script is run directly from a release archive.
PROJECT_ROOT = os.path.realpath(os.path.join(os.pardir, os.pardir))
sys.path.insert(0, PROJECT_ROOT)

from pyaixi import util

# An enumeration type used to specify the type of Monte Carlo search node.
# Chance nodes represent sets of possible observations (one child per observation).
# Decision nodes represent sets of possible actions (one child per action).
# Decision and chance nodes alternate.
nodetype_enum = util.enum('chance', 'decision')

# Defines some shortcuts for ease of reference.
chance_node = nodetype_enum.chance
decision_node = nodetype_enum.decision


class MonteCarloSearchNode:
    """ A class to represent a node in the Monte Carlo search tree.

        The nodes in the search tree represent simulated actions and percepts
        between an agent following an upper confidence bounds (UCB) policy and a generative
        model of the environment represented by a context tree.

        The purpose of the tree is to determine the expected reward of the
        available actions through sampling. Sampling proceeds several time steps
        into the future according to the size of the agent's horizon.
        (`MC_AIXI_CTW_Agent.horizon`)

        The nodes are one of two types (`nodetype_enum`):
         - Decision nodes have children chance nodes, linked by agent actions.
         - Chance nodes have child decision nodes, linked by environmental percepts.

        Each MonteCarloSearchNode maintains several bits of information:

          - The current value of the sampled expected reward
            (`MonteCarloSearchNode.mean`, `MonteCarloSearchNode.expectation`).

          - The number of times the node has been visited during the sampling
            (`MonteCarloSearchNode.visits`).

          - The type of the node (MonteCarloSearchNode.type).

          - The children of the node (`MonteCarloSearchNode.children`).
            The children are stored in a dictionary indexed by action (if
            it is a decision node) or percept (if it is a chance node).

        The `MonteCarloSearchNode.sample` method is used to sample from the current node and
        the `MonteCarloSearchNode.selectAction` method is used to select an action according
        to the UCB policy.
    """

    # Class attributes.

    # Exploration constant for the UCB action policy.
    exploration_constant = math.sqrt(2.0)

    # Instance methods.

    def __init__(self, nodetype):
        """ Create a new search node of the given type.
        """

        # The type of this node indicates whether its children represent actions
        # (decision node) or percepts (chance node).
        assert nodetype in nodetype_enum, "The given value %s is a not a valid node type." % str(nodetype)
        self.type = nodetype

        # The children of this node.
        # The symbols used as keys at each level may be either action or observation,
        # depending on what type of node this is.
        self.children = {}

        # The sampled expected reward of this node.
        self.mean = 0.0

        # The number of times this node has been visited during sampling.
        self.visits = 0
    # end def

    def sample(self, agent, horizon):
        """
        Performs one iteration of the MC tree loop: select, rollout, update.
        Returns the accumulated reward below this node.

            - `agent`: the agent doing the sampling
            - `horizon`: how many steps into the future to sample
        """

        reward_sum = 0.0
        agent.set_savestate()

        if horizon == 0:
            print("reached horizon")
            assert self.type == decision_node
            return 0.0

        elif self.type == chance_node:
            print("sample percept")
            # sample or from ρ(or|h)
            observation, reward = agent.generate_percept_and_update()

            # create node hor if it is an unvisited child.
            if not (observation in self.children):
                self.children[observation] = MonteCarloSearchNode(decision_node)
            # end if

            child = self.children[observation]
            # TODO: decide if it should be (observation, reward)
            # Algorithm 2 of [Veness, 2011].
            reward_sum = reward + self.sample(child, agent, horizon - 1)

        elif self.visits == 0:
            print("havent visited node before")
            reward_sum = agent.playout(horizon)

        else:
            print("select action")
            action = self.select_action(agent, horizon)
            agent.model_update_action(action)
            reward_sum = self.sample(agent, horizon)

        # end if

        agent.restore_savestate()

        self.mean = (reward_sum + self.mean * self.visits)/(self.visits + 1)
        self.visits = self.visits + 1

        return reward_sum
    # end def

    def sample_iterations(self, agent, horizon, iterations):
        """ Performs sampling for many iterations at this node.

            - `agent`: the agent doing the sampling
            - `horizon`: how many steps into the future to sample
            - `iterations`: how many iterations to perform
        """

        for i in range(iterations):
            self.sample(agent, horizon)
    # end def

    def select_action(self, agent, horizon):
        """ Returns an action selected according to UCB policy.

             - `agent`: the agent which is doing the sampling.
             - `horizon`: how many steps into the future to sample
        """

        assert self.type == decision_node

        tried_actions = self.children.keys()
        all_actions = agent.generate_all_actions()
        untried_actions = list(set(all_actions) - set(tried_actions))

        if untried_actions:  # If there are untried actions
            action = random.choice(untried_actions) # choose a random untried action
            self.children[action] = MonteCarloSearchNode(chance_node) # add it as a new MCTS node
            return action # return this action
        # end if

        assert len(untried_actions) == 0, "All children should have been visited."

        # No untried actions. Use UCB to find the best action.
        action_ucb = {}
        reward_range = agent.range_of_reward()
        for action in all_actions:
            child = self.children[action]
            # NOTE: Still not sure if it should divide by (horizon * reward_range)
            action_ucb[action] = (child.value / reward_range
                + self.exploration_constant * math.sqrt(math.log(self.visits) / child.visits))

        # end for

        # now pick the action with the highest UCD score.
        best_action = max(action_ucb, key=action_ucb.get)
        return best_action
    # end def

# end class


def mcts_planning(agent, horizon, iterations):
    """ Run the ρUCT planning algorithm for a given number of iterations with a
        given horizon distance, and return the best action found.

        - `agent`: the agent doing the sampling
        - `horizon`: how many cycles into the future to sample
        - `iterations`: how many samples to take
    """
    mc_tree = MonteCarloSearchNode(decision_node)
    mc_tree.sample_iterations(agent, horizon, iterations)
    return mc_tree.select_action(agent, horizon)
# end def
