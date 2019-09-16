#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Defines an environment for AIXI agents.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sys
from pyaixi import util

class Environment:
    """ Base class for the various agent environments.

        Each individual environment should inherit from this class and implement the appropriate methods.

        In particular, the constructor should set up the environment as appropriate, including
        setting the initial observation and reward, as well as setting appropriate
        values for the configuration options:
         - `agent-actions`
         - `observation-bits`
         - `reward-bits`

        Following this, the agent and environment interact in a cyclic fashion. The
        agent receives the observation and reward using `Environment.getObservation`
        and `Environment.getReward` before supplying the environment with an action
        via `Environment.performAction`.

        Upon receiving an action, the environment updates the observation and reward.
        At the beginning of each cycle, the value of `Environment::isFinished` is checked.

        If it is true then there is no more interaction between the agent and environment,
        and the program exits. Otherwise the interaction continues indefinitely.
    """

    def __init__(self, options = {}):
        """ Construct an agent environment.
        """

        # Set the current action to null/None.
        self.action = None

        # Set whether the environment is finished.
        self.is_finished = False

        # Set the current observation to null/None.
        self.observation = None

        # Store the given options.
        self.options = options

        # Set the current reward to null/None.
        self.reward = None

        # Defines the acceptable action values.
        self.valid_actions = []

        # Define the acceptable observation values.
        self.valid_observations = []

        # Define the acceptable reward values.
        self.valid_rewards = []
    # end def

    def __unicode__(self):
        """ Returns a string representation of this environment instance.
        """
        return "action = " + str(self.action) + ", observation = " + \
               str(self.observation) + ", reward = " + str(self.reward)
    # end def

    # Make a compatible string function for the current Python version.
    if sys.version_info[0] >= 3:
        # For Python 3.
        def __str__(self):
            return self.__unicode__()
        # end def
    else:
        # For Python 2.
        def __str__(self):
            return self.__unicode__().encode('utf8')
        # end def
    # end def

    def action_bits(self):
        """ Returns the maximum number of bits required to represent an action.
        """

        # TODO: implement

        return None
    # end def

    def is_valid_action(self, action):
        """ Returns whether the given action is valid.
        """
        # TODO: implement
        return None
    # end def

    def is_valid_observation(self, observation):
        """ Returns whether the given observation is valid.
        """
        # TODO: implement
        return None
    # end def

    def is_valid_reward(self, reward):
        """ Returns whether the given reward is valid.
        """
        # TODO: implement
        return None
    # end def

    def maximum_action(self):
        """ Returns the maximum possible action.
        """

        # TODO: implement
        return None
    # end def

    def maximum_observation(self):
        """ Returns the maximum possible observation.
        """

        # TODO: implement
        return None
    # end def

    def maximum_reward(self):
        """ Returns the maximum possible reward.
        """

        # TODO: implement
        return None
    # end def

    def minimum_action(self):
        """ Returns the minimum possible action.
        """

        # TODO: implement
        return None
    # end def

    def minimum_observation(self):
        """ Returns the minimum possible observation.
        """

        # TODO: implement
        return None
    # end def

    def minimum_reward(self):
        """ Returns the minimum possible reward.
        """

        # TODO: implement
        return None
    # end def

    def observation_bits(self):
        """ Returns the maximum number of bits required to represent an observation.
        """

        # TODO: implement

        return None
    # end def

    def percept_bits(self):
        """ Returns the maximum number of bits required to represent a percept.
        """
        # TODO: implement

        return None
    # end def

    def perform_action(self, action):
        """ Receives the agent's action and calculates the new environment percept.
        """
        # TODO: implement
    # end def

    def print(self):
        """ String representation convenience method from the C++ version.
        """
        # TODO: implement
        return None
    # end def

    def reward_bits(self):
        """ Returns the maximum number of bits required to represent a reward.
        """

        # TODO: implement

        return None
    # end def
# end class
