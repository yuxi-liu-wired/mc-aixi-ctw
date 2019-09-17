#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Defines a class to implement a Monte Carlo search tree.
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
    exploration_constant = 2.0

    # Unexplored action bias.
    unexplored_bias = 1000000000.0

    # Instance methods.

    def __init__(self, nodetype):
        """ Create a new search node of the given type.
        """

        # The children of this node.
        # The symbols used as keys at each level may be either action or observation,
        # depending on what type of node this is.
        self.children = {}

        # The sampled expected reward of this node.
        self.mean = 0.0

        # The type of this node indicates whether its children represent actions
        # (decision node) or percepts (chance node).
        assert nodetype in nodetype_enum, "The given value %s is a not a valid node type." % str(nodetype)
        self.type = nodetype

        # The number of times this node has been visited during sampling.
        self.visits = 0
    # end def

    def sample(self, agent, horizon):
        """ Returns the accumulated reward from performing a single sample on this node.

            - `agent`: the agent doing the sampling

            - `horizon`: how many cycles into the future to sample
        """

        # TODO: implement
        reward = 0.0


        return reward
    # end def

    def select_action(self, agent):
        """ Returns an action selected according to UCB policy.

             - `agent`: the agent which is doing the sampling.
        """

        # TODO: implement
        best_action = None


        return best_action
    # end def
# end class
