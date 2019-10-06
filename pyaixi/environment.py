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
         - initial observation
         - initial reward
        as well as setting appropriate values for the configuration options:
         - `agent-actions`
         - `observation-bits`
         - `reward-bits`

        Following this, the agent and the environment interact in a cyclic fashion.
        In each cycle, the agent does three things:
         - receives the observation using `Environment.getObservation`
         - receives the reward using `Environment.getReward`
         - sending an action to the environment using `Environment.performAction`.

        Upon receiving an action, the environment updates:
         - observation
         - reward

        At the beginning of each cycle, the value of `Environment::isFinished` is checked.
        If true, then there is no more interaction between the agent and environment,
        and the program exits. This can be thought of as the death of the agent.
        Otherwise the interaction continues.
    """

    def __init__(self, options = {}):
        """ Constructs an agent environment.
        """

        # Set whether the environment is finished.
        self.is_finished = False

        # Store the given options.
        self.options = options

        # Set the current action to null/None.
        self.action = None

        # Set the current observation to null/None.
        self.observation = None

        # Set the current reward to null/None.
        self.reward = None

        # Define the acceptable action values.
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

    # Makes a compatible string function for the current Python version.
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
    # end if

    def is_valid_action(self, action):
        """ Returns whether the given action is valid.
        """

        if(action in self.valid_actions):
            return True
        else:
            return False
    # end def

    def is_valid_observation(self, observation):
        """ Returns whether the given observation is valid.
        """

        if(observation in self.valid_observations):
            return True
        else:
            return False
    # end def

    def is_valid_reward(self, reward):
        """ Returns whether the given reward is valid.
        """

        if(reward in self.valid_rewards):
            return True
        else:
            return False
    # end def

    def maximum_action(self):
        """ Returns the maximum possible action.
        """

        return max(self.valid_actions)
    # end def

    def maximum_observation(self):
        """ Returns the maximum possible observation.
        """

        # TODO: implement
        return max(self.valid_observations)
    # end def

    def maximum_reward(self):
        """ Returns the maximum possible reward.
        """

        return max(self.valid_rewards)
    # end def

    def minimum_action(self):
        """ Returns the minimum possible action.
        """

        return min(self.valid_actions)
    # end def

    def minimum_observation(self):
        """ Returns the minimum possible observation.
        """

        return min(self.valid_observations)
    # end def

    def minimum_reward(self):
        """ Returns the minimum possible reward.
        """

        return min(self.valid_rewards)
    # end def

    def action_bits(self):
        """ Returns the maximum number of bits required to represent an action.
        """

        actions = [util.bits_required(action) for action in self.valid_actions]

        return max(actions)
    # end def

    def observation_bits(self):
        """ Returns the maximum number of bits required to represent an observation.
        """

        observations = [util.bits_required(obs) for obs in self.valid_observations]

        return max(observations)
    # end def

    def percept_bits(self):
        """ Returns the maximum number of bits required to represent a percept.
        """

        return self.observation_bits()+self.reward_bits()
    # end def

    def reward_bits(self):
        """ Returns the maximum number of bits required to represent a reward.
        """

        return util.bits_required(self.reward)
    # end def

    def perform_action(self, action):
        """ Receives the agent's action and calculates the new environment percept.
        """

        self.action = action
    # end def

    def print(self):
        """ String representation convenience method from the C++ version.
        """
        print('what ')
        return None
    # end def

# end class
