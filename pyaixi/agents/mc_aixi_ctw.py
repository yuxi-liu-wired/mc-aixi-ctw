#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Defines a class for the MC-AIXI-CTW agent.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import copy
import os
import random
import sys

# Insert the package's parent directory into the system search path, so that this package can be
# imported when the aixi.py script is run directly from a release archive.
PROJECT_ROOT = os.path.realpath(os.path.join(os.pardir, os.pardir))
sys.path.insert(0, PROJECT_ROOT)

# Ensure xrange is defined on Python 3.
from six.moves import xrange

from pyaixi import agent, prediction, util

from pyaixi.agent import update_enum, action_update, percept_update
from pyaixi.prediction import ctw_context_tree
from pyaixi.search.monte_carlo_search_tree import MonteCarloSearchNode


class MC_AIXI_CTW_Undo:
    """ A class to save details from a MC-AIXI-CTW agent to restore state later.
    """

    # Instance methods.

    def __init__(self, agent):
        """ Store values from the given agent that can be used to revert that agent to a previous state.
        """

        # Copy the main attributes of the given agent into this class.
        self.age = agent.age
        self.total_reward = agent.total_reward
        self.history_size = agent.history_size()
        self.last_update = agent.last_update
    # end def
# end class


class MC_AIXI_CTW_Agent(agent.Agent):
    """ This class represents a MC-AIXI-CTW agent.

        It includes much of the high-level logic for choosing suitable actions.
        In particular, the agent maintains an internal model of the environment using
        a context tree.

        It uses this internal model to to predict the probability of future outcomes:

         - `get_predicted_action_probability()`
         - `percept_probability()`

        as well as to generate actions and precepts according to the model distribution:

         - `generate_action()`: sample next action from the CTW model
         - `generate_percept()`: sample next percept from the CTW model
         - `generate_percept_and_update()`:
                sample next percept from the CTW model, and update the CTW model with the sampled percept
         - `generate_random_action()`: sample next action uniformly randomly

        Actions are chosen via the UCT algorithm, which is orchestrated by a
        high-level search function and a playout policy:

         - `search()`
         - `playout()`
         - `horizon`
         - `mc_simulations`
         - `search_tree`

        Several functions decode/encode actions and percepts between the
        corresponding types (i.e. `action_enum`, `percept_enum`) and generic
        representation by symbol lists:

         - `decode_action()`
         - `decode_observation()`
         - `decode_reward()`
         - `decode_percept()`
         - `encode_action()`
         - `encode_percept()`

        There are various attributes which describe the agent and its
        interaction with the environment so far:

         - `age`
         - `average_reward`
         - `history_size()`
         - `horizon`
         - `last_update`
         - `maximum_action()`
         - `maximum_bits_needed()`
         - `maximum_reward()`
         - `total_reward`
    """

    # Instance methods.

    def __init__(self, environment = None, options = {}):
        """ Construct a MC-AIXI-CTW learning agent from the given configuration values and the environment.

             - `environment` is an instance of the pyaixi.Environment class that the agent interact with.
             - `options` is a dictionary of named options and their values.

            `options` must contain the following mandatory options:
             - `agent-horizon`: the agent's planning horizon.
             - `ct-depth`: the depth of the context tree for this agent, in symbols/bits.
             - `mc-simulations`: the number of simulations to run when choosing new actions.

            The following options are optional:
             - `learning-period`: the number of cycles the agent should learn for.
                                  Defaults to '0', which is indefinite learning.
        """

        # Sets up the base agent options, which handles getting and setting the
        # learning period, amongst other basic values.
        agent.Agent.__init__(self, environment = environment, options = options)

        # The agent's context tree depth.
        # Retrieved from the given options under 'ct-depth'. Mandatory.
        assert 'ct-depth' in options, \
               "The required 'ct-depth' context tree depth option is missing from the given options."
        self.depth = int(options['ct-depth'])

        # (CTW) Context tree representing the agent's model of the environment.
        # Created for this instance.
        self.context_tree = ctw_context_tree.CTWContextTree(self.depth)

        # The length of the agent's planning horizon.
        # Retrieved from the given options under 'agent-horizon'. Mandatory.
        assert 'agent-horizon' in options, \
               "The required 'agent-horizon' search horizon option is missing from the given options."
        self.horizon = int(options['agent-horizon'])

        # The number of simulations to conduct when choosing new actions via the UCT algorithm.
        # Retrieved from the given options under 'mc-simulations'. Mandatory.
        assert 'mc-simulations' in options, \
               "The required 'mc-simulations' Monte Carlo simulations count option is missing from the given options."
        self.mc_simulations = int(options['mc-simulations'])

        self.reset()

        # Saves a state of the agent that allows restoring the savestate.
        self.savestate = MC_AIXI_CTW_Undo(self)
    # end def

    ## Decoders and encoders.
    def decode_action(self, symbol_list):
        """ Returns the action decoded from the beginning of the given list of symbols.

            - `symbol_list`: the symbol list to decode the action from.
        """

        return util.decode(symbol_list, self.environment.action_bits())
    # end def

    def decode_observation(self, symbol_list):
        """ Returns the observation decoded from the given list of symbols.

            - `symbol_list`: the symbol list to decode the observation from.
        """

        return util.decode(symbol_list, self.environment.observation_bits())
    # end def

    def decode_reward(self, symbol_list):
        """ Returns the reward decoded from the beginning of the given list of symbols.

            - `symbol_list`: the symbol list to decode the reward from.
        """

        return util.decode(symbol_list, self.environment.reward_bits())
    # end def

    def decode_percept(self, symbol_list):
        """ Returns the percept (observation and reward) decoded from the beginning of
            the given list of symbols.

            - `symbol_list`: the symbol list to decode the percept from.
        """

        # Check if we've got exactly enough symbols.
        reward_bits = self.environment.reward_bits()
        observation_bits = self.environment.observation_bits()

        assert len(symbol_list) >= (reward_bits + observation_bits),\
               "The given symbol list isn't long enough to contain a percept."

        # Get the reward symbols from the given symbol list, starting with the
        # reward, then getting the observation from the list after that.
        reward_symbols      = symbol_list[:reward_bits]
        observation_symbols = symbol_list[reward_bits:(reward_bits + observation_bits)]

        # Decode the obtained symbols.
        reward      = self.decode_reward(reward_symbols)
        observation = self.decode_observation(observation_symbols)

        # Return the decoded percept as a tuple of observation and reward.
        return (observation, reward)
    # end def

    def encode_action(self, action):
        """ Returns the given action encoded as a list of symbols.

            - `action`: the action to encode.
        """

        return util.encode(action, self.environment.action_bits())
    # end def

    def encode_percept(self, observation, reward):
        """ Returns the given percept (an observation, reward part) as a list of symbols.

            - `observation`: the observation part of the percept to encode.
            - `reward`: the reward part of the percept to encode.
        """

        # Add first the encoded reward, then the encoded observation to the list of output symbols.
        symbol_list  = util.encode(reward, self.environment.reward_bits())
        symbol_list += util.encode(observation, self.environment.observation_bits())

        # Return the generated list.
        return symbol_list
    # end def

    ## Predict future history using CTW.
    def generate_action(self):
        """ Returns an action, distributed according to the agent's history
            statistics, by sampling from the context tree.
        """

        assert self.last_update == percept_update,  "Can only generate an action after a percept update."

        action_bit_count = self.environment.action_bits()
        action_bits = self.context_tree.generate_random_symbols(action_bit_count)
        return self.decode_action(action_bits)
    # end def

    def generate_percept(self):
        """ Returns a percept (observation, reward), distributed according to the agent's history
            statistics, by sampling from the context tree.
        """

        assert self.last_update == action_update,  "Can only generate a percept after an action update."

        percept_bit_count = self.environment.percept_bits()
        percept_bits = self.context_tree.generate_random_symbols(percept_bit_count)
        return self.decode_percept(percept_bits)
    # end def

    def generate_percept_and_update(self):
        """ Generates a percept (observation, reward), distributed according to the agent's history
            statistics, then updates the context tree with it, and return it.
            THe percept would update parameters the context tree (learning) iff the agent is still learning.
            otherwise, it would only update the history of the context tree.
        """

        assert self.last_update == action_update,  "Can only perform a percept update after an action update."
        observation, reward = self.generate_percept()
        self.model_update_percept(observation, reward)
        # Note that this would cause learning iff the agent is still learning
        return observation, reward
    # end def

    ## Inquire its model for probability of future.
    # TODO: what is this for?
    def action_probability(self, action):
        """ Returns the probability of selecting a particular action according to the
            agent's internal model of its own behaviour.

            - `action`: the action we wish to find the likelihood of.
        """

        return self.context_tree.predict(self.encode_action(action))
    # end def

    # TODO: what is this for?
    def percept_probability(self, observation, reward):
        """ Returns the probability of receiving percept (observation, reward),
            according to the agent's environment model.

            - `observation`: the observation part of the percept we wish to find the likelihood of.
            - `reward`: the reward part of the percept we wish to find the likelihood of.
        """

        return self.context_tree.predict(self.encode_percept(observation, reward))
    # end def

    def history_size(self):
        """ Returns the length of the stored history for an agent.
        """

        return len(self.context_tree.history)
    # end def

    # TODO: what is this for?
    def maximum_bits_needed(self):
        """ Returns the maximum number of bits needed to represent actions or percepts.
            NOTE: this is for binary alphabets.
        """

        return max(self.environment.action_bits(), self.environment.percept_bits())
    # end def

    ## For saving and loading the agent state.
    def model_revert(self, undo_instance):
        """ Revert the agent's internal environment model to that of a previous time cycle,
            using the given undo class instance.
        """

        self.age = undo_instance.age
        self.total_reward = undo_instance.total_reward
        self.last_update = undo_instance.last_update

        old_history_size = undo_instance.history_size
        current_history_size = self.history_size()
        if current_history_size > old_history_size:
            self.context_tree.revert(current_history_size - old_history_size)
    # end def

    def set_savestate(self):
        """ Sets a savestate that can later be restored.
        """
        self.savestate = MC_AIXI_CTW_Undo(self)
    # end def

    def restore_savestate(self):
        self.model_revert(self.savestate)
    # end def

    def model_size(self):
        """ Returns the size of the agent's model.
        """
        return self.context_tree.size()
    # end def

    def model_update_action(self, action):
        """ Updates the agent's environment model with an action.

            - `action`: the action that the agent performed.
        """

        # The action must be valid.
        assert self.environment.is_valid_action(action), "Invalid action given."

        # The last update must have been a percept, else this action update is invalid.
        assert self.last_update == percept_update, "Can only perform an action update after a percept update."

        # Update the agent's internal environment model after performing an action.

        # Get the symbols that represent this action.
        action_symbols = self.encode_action(action)

        # Update the context tree.
        self.context_tree.update_history(action_symbols)

        # Update other properties.
        self.age += 1
        self.last_update = action_update
    # end def

    def model_update_percept(self, observation, reward):
        """ Updates the agent's environment model with percept (observation, reward)
            from the environment.

            - `observation`: the observation that was received.
            - `reward`: the reward that was received.
        """

        # The last update must have been an action, else this percept update is invalid.
        assert self.last_update == action_update, "Can only perform a percept update after an action update."

        # Update the internal model after performing a percept.

        # Get the symbols that represent this percept from the given observation and reward.
        percept_symbols = self.encode_percept(observation, reward)

        # Are we still meant to be learning?
        if ((self.learning_period > 0) and (self.age > self.learning_period)):
            # No. Update, but don't learn.
            self.context_tree.update_history(percept_symbols)
        else:
            # Yes. Update and learn.
            self.context_tree.update(percept_symbols)
        # end if

        # Update other properties.
        self.total_reward += reward
        self.last_update = percept_update
    # end def

    def playout(self, horizon):
        """ Simulates agent/enviroment interaction for a specified amount of steps
            (the given horizon value) where the agent actions are chosen uniformly
            at random and percepts are generated. After the playout, revert the
            agent state to before playout.

            Returns the total reward from the simulation.

            - `horizon`: the number of complete action/percept steps
                         (the search horizon) to simulate.
        """

        reward_sum = 0.0
        self.set_savestate()

        for i in range(horizon):
            if self.environment.is_finished:
                break
            # note that generate_action() generates according to the past
            # while generate_random_action() generates randomly uniformly
            self.model_update_action(self.generate_random_action())
            _, reward = self.generate_percept_and_update()
            reward_sum += reward
        # end for

        self.restore_savestate()
        return reward_sum
    # end def

    def reset(self):
        """ Resets the agent and clears the context tree.
        """

        # Clears the context tree.
        self.context_tree.clear()

        # Resets the basic agent details: age, total_reward, last_update.
        agent.Agent.reset(self)
    # end def

    def search(self):
        """ Returns the best action for this agent as determined using the Monte-Carlo Tree Search
            (predictive UCT).
        """

        # Use ρUCT to search for the next action.
        best_action = MonteCarloSearchNode.mcts_planning(self, self.horizon, self.mc_simulations)
        return best_action
    # end def
# end class
