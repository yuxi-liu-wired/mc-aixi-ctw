#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 24 22:20:04 2019

@author: Yan
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from pyaixi import environment, util
import os
import random
import sys
import numpy as np

# Insert the package's parent directory into the system search path, so that this
# package can be imported when the aixi.py script is run directly from a release archive.
PROJECT_ROOT = os.path.realpath(os.path.join(os.pardir, os.pardir))
sys.path.insert(0, PROJECT_ROOT)

# map of Pacman.
layout_txt = "pacMan.txt"
# a food pellet is placed with probability 0.5 at every empty location on the map.
default_probability = 0.5

# Define the enumerations to represents the observations and actions
pacman_action_enum = util.enum('top', 'down', 'left', 'right')
pacman_wall_observations_enum = util.enum(wNull=0, wTopWall=1, wDownWall=2,
                                          wLeftWall=4, wRightWall=8)
pacman_ghost_observation_enum = util.enum(gNull=0, gTopWall=16, gDownWall=32,
                                          gLeftWall=64, gRightWall=128)

pacman_smell_observation_enum = util.enum(
    mD_n=0, mD_2=256, mD_3=512, mD_4=1024)
smell_constant = 4
pacman_sight_observation_enum = util.enum(sNull=0, sTop=2048, sDown=4096,
                                          sLeft=8192, sRight=16384)
pacman_power_observation_enum = util.enum(withouEffect=0, underEffect=32768)

# Predefined dictionary to help us perform the actions.
direction = {
    '0': [1, 0],  # top
    '1': [-1, 0],  # down
    '2': [0, -1],  # left
    '3': [0, 1]  # right
}

direction_list = list(direction.values())

rule = {
    "movement": -1,
    "wall": -10,
    "pellet": 10,
    "caught": -50,
    "all": 100,
    "pill": 10,
    "eat_g": 30
}

compensation = sum([abs(v) for v in rule.values() if v < 0])


class PacMan(environment.Environment):
    ''' The Pacman environment.

        The layout file uses the format:
            * = pellet
            % = wall
              = empty space
            P = Pacman
            S = power pill
            other letters = ghosts
        The magic channels are written in the bottom rows, in the format:
            (x1,y1)!(x2,y2)

        Attributes
        ----------

        rows : int, default 0
            denotes the number of rows in the layout

        cols : int, default 0
            denotes the number of columns in the layout

        magic_channel : dict()
            a dictionary representing magic channels, with one location (x, y)
            mapping to a valid loation (x_1, y_1):
            magic_channel[x,y] = [x_1,y_1]

        max_rewards : int
            denotes the maximum number of rewards the agent could earn

        pellets_remaining : int, default 0
            denotes the number of pellets remain on the map

        max_observation : int, default 2**16.
            deonotes the largest obersvation value

        layout : [[]]
            a 2d list representing the game map

        ghost : dict()
            a dictionary of type {ghost name : ghost location}

        power_pill : []
            a list of the location of remaining power pill on the map.

        pacman : [a,b]  a,b belongs to N
            pacman location

        reward : int, default 0
            a nonnegative integer denoting the score in the current round

        is_finished : bool, default False
            if the enviroments is finished

        super_pacman : bool, default False
            if the Pacman is under the effect of power pill

        super_pacman_time: int, default 0
            remaining time of Pacman under the effect of power pill.

        valid_rewards : range
            a range of all valid rewards

        valid_actions: []
            a list of all valid actions

        valid_observations: range
            a range of valid observations

        observations : int
            code of the current obervation of the agent

        actions: int
            code of the action the agent just taken.
    '''

    def __init__(self, options={}):
        ''' Initialize the setup for Pacman.
        '''

        self.max_reward = sum(map(lambda x: abs(x), rule.values()))
        self.valid_rewards = range(self.max_reward)
        self.valid_actions = list(pacman_action_enum.keys())
        self.max_observation = 2**16
        self.valid_observations = range(self.max_observation)

        self.action = None
        self.restart()
        self.reward = 0

    def restart(self):
        ''' Start a new game.
        '''
        self.rows = 0
        self.cols = 0
        self.magic_channel = dict()
        self.pellets_remaining = 0
        self.max_observation = 2**16
        self.layout = self.load(layout_txt)

        self.initialize_layout()
        self.ghost_names = set(self.ghost.keys())
        self.is_finished = False
        self.super_pacman = False
        self.super_pacman_time = 0
        self.observation = self.calculate_observation()

    def random_pellets(self, x):
        """ On an empty location (' '), generate a pellet with default_probability.

        Parameters
        ----------
        x : string
            the symbol of a location on the map.

        Returns
        -------
        string  "*" or x, where "*" denotes a pellet.
        """

        if x == ' ' and random.random() < default_probability:
            return "*"
        else:
            return x

    def load(self, layout):
        """ Loads the file that contains the map, and generates pellets randomly
            on its empty spaces. Also sets rows and columns to the attribute.

        Parameters
        ----------
        layout : string
            map file name

        Returns
        -------
        pacman_map : [[]]
            a 2d list representation of the map
        """

        # based on https://stackoverflow.com/questions/50499/how-do-i-get-the-path-and-name-of-the-file-that-is-currently-executing
        import inspect
        sep = '/' if '/' in PROJECT_ROOT else '\\'
        path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) + sep + layout

        pacman_map = []
        with open(path) as f:
            lines = f.readlines()
            for line in lines:
                if "!" in line: # Magic channels.
                    a, b = line.strip().split("!")
                    a = eval(a)
                    b = eval(b)
                    self.magic_channel[a] = b
                    continue

                # Generate random pellets on all empty spaces on the map.
                line = list(map(self.random_pellets, line))
                line.remove("\n")
                self.pellets_remaining += line.count("*") # Count total pellets.
                pacman_map.append(line)

        # Width and length of the map.
        self.rows = len(pacman_map)
        self.cols = len(pacman_map[0])
        return pacman_map

    def initialize_layout(self):
        """ Parse the layout map and store the locations of Pacman, power pills,
            and ghosts. Keeps the walls and pellets on the layout map
            to execute action of Pacman and movements of ghosts.
        """

        self.pacman = None
        self.power_pill = []
        self.ghost = {}
        for row in range(len(self.layout)):
            for col in range(len(self.layout[0])):
                char = self.layout[row][col]
                if char == "P":
                    self.pacman = [row, col]
                    self.layout[row][col] = " " # It leaves behind a hole.
                elif char == "S":
                    self.power_pill.append([row, col])
                elif char.isalpha():
                    self.ghost[char] = [row, col]
        for name, positon in self.ghost.items():
            x, y = positon
            self.layout[x][y] = " "

    def perform_action(self, action):
        """ Perform Pacman's action, update the map, move ghosts, update
            observation and reward.

            The caculation of rewards follow these rules:
                1. -1 for each successful movement.
                2. -10 for running into a wall, which does not move the Pacman.
                3. +10 for each food pellet eaten
                4. -50 for being caught by a ghost
                5. +100 for collecting all the food
                6. +10 for eating a power pill.
                7. +30 for eating a ghost while on a power pill effect, which
                   also reset the position of ghost.
            The scores are positivized by adding 50.

        Parameters
        ----------
        action : string
            the code for the actions

        Returns
        -------
        reward : int
            the current reward for pacman
        observation: int
            the current obervations for pacman
        """

        self.action = action
        self.reward = compensation # Added to ensure reward is nonnegative.

        # Movement reward.
        self.reward += rule["movement"]

        # Calculate new position of Pacman.
        old_x, old_y = self.pacman # Old position
        dx, dy = direction[str(action)] # Difference in position
        x, y = old_x + dx, old_y + dy # New position
        # Check if the Pacman is transported through the magic channel.
        if (x, y) in self.magic_channel:
            x, y = self.magic_channel[x, y]
        map_symbol = self.layout[x][y] # Map symbol of the new Pacman position.
        if map_symbol == "%": # Pacman went into a wall.
            self.reward += rule["wall"]
            x, y = self.pacman # Move back to previous location
        else: # Pacman did not go into a wall.
            self.pacman = x, y # The motion succeeds.
            # self.layout[old_x][old_y] = " " # The previous location is vacated.

        if map_symbol == "*": # Pacman eats a pellet.
            self.reward += rule["pellet"]
            self.layout[x][y] = " "
            self.pellets_remaining -= 1

        if [x, y] in self.ghost.values():
        # Pacman went into a ghost (which could be standing on a pallet).
            if self.super_pacman: # Super Pacman eats the ghost.
                self.reward += rule["eat_g"]

                # Find the name of the ghost eaten.
                for name, location in self.ghost.items():
                    if location == [x, y]:
                        break

                # Respawn at a random non-wall, non-ghost, non-Pacman location.
                while True:
                    m_x = random.randint(0, self.rows - 1)
                    m_y = random.randint(0, self.cols - 1)
                    if self.layout[m_x][m_y] != "%" and [m_x, m_y] not in self.ghost.values():
                        # Note that Pacman's location happens to be equal to the
                        # eaten ghost, so this cleverly handles avoiding Pacman!
                        break
                self.ghost[name] = [m_x, m_y] # Respawn

            else: # Ghost eats Pacman, game ends.
                self.reward += rule["caught"]
                self.restart()
                return self.reward, self.observation

        # If non-super Pacman moves to a powerpill occupied by a ghost, then
        # Pacman dies before it could eat the powerpill. Sad!
        if map_symbol == "S": # Eats a powerpill.
            self.reward += rule["pill"]
            self.super_pacman = True
            self.super_pacman_time += 100 # 100 timesteps of super Pacman.
            self.layout[x][y] = " " # Empties the location.
            self.power_pill.remove([x, y])

        # Updates super pacman status.
        if self.super_pacman_time > 0:
            self.super_pacman_time -= 1
        if self.super_pacman_time == 0:
            self.super_pacman = False # Loses super Pacman status.

        # All pellets eaten, game ends.
        if self.pellets_remaining == 0:
            self.reward += rule["all"]
            self.restart()
            return self.reward, self.observation

        # If game is still in progress, then move all the ghosts.
        self.move_ghost()

        # Update agent observation.
        self.observation = self.calculate_observation()
        return self.reward, self.observation

    def calculate_observation(self):
        ''' Observations are encoded according to the rules below:

            1. 4 bits describing wall/no wall in the four neighbors of Pacman.
            2. 4 bits indicating whether a ghost is visible to Pacman (via
               direct line of sight) in each of the four cardinal directions.
            3. 3 bits indicating whether at least one pellet exists within a
               Manhattan distance of 2, 3 or 4 from PacMan’s location,
            4. 4 bits indicating whether a pallet is visible to Pacman (via
               direct line of sight) in each of the four cardinal directions.
            5. 1 bit indicating whether PacMan is under the effects of a power pill.

        Parameters
        ----------
        None

        Returns
        -------
        observation: int
            binary code of observation, converted to an int
        '''

        observation = 0

        p_x, p_y = self.pacman

        layout = np.array(self.layout)
        shadow_layout = np.array(self.layout)

        # Observe the walls.
        for key, loc in direction.items():
            x, y = loc
            new_x, new_y = p_x + x, p_y + y

            if (new_x, new_y) in self.magic_channel:
                new_x, new_y = self.magic_channel[new_x, new_y]

            if self.layout[new_x][new_y] == "%":
                observation += 2**(int(key))

        # Observe the ghosts.
        for name, loc in self.ghost.items():
            x, y = loc
            shadow_layout[x, y] = name

        if self.ghost_names.intersection(shadow_layout[p_x, p_y:]):
            # right,including at same position
            for name in self.ghost_names.intersection(shadow_layout[p_x, p_y:]):
                m_x, m_y = self.ghost[name]
                # No walls in sight
                if "%" not in shadow_layout[p_x, p_y:m_y]:
                    observation += pacman_ghost_observation_enum.gRightWall
                    break

        if self.ghost_names.intersection(shadow_layout[p_x, :p_y]):
            # left

            for name in self.ghost_names.intersection(shadow_layout[p_x, :p_y]):
                m_x, m_y = self.ghost[name]
                # No walls in sight
                if "%" not in shadow_layout[p_x, m_y:p_y]:
                    observation += pacman_ghost_observation_enum.gLeftWall
                    break

        if self.ghost_names.intersection(shadow_layout[:p_x, p_y]):
            # down
            for name in self.ghost_names.intersection(shadow_layout[:p_x, p_y]):
                m_x, m_y = self.ghost[name]
                # no wall in the sight
                if "%" not in shadow_layout[m_x:p_x, p_y]:
                    observation += pacman_ghost_observation_enum.gDownWall
                    break

        if self.ghost_names.intersection(shadow_layout[p_x + 1:, p_y]):
            # top
            for name in self.ghost_names.intersection(shadow_layout[p_x + 1:, p_y]):
                m_x, m_y = self.ghost[name]
                # No walls in sight
                if "%" not in shadow_layout[p_x + 1:m_x, p_y]:
                    observation += pacman_ghost_observation_enum.gTopWall
                    break

        # Smell the pellets.
        smelled_pill_distances = set()
        for x, line in enumerate(self.layout):
            for y, symbol in enumerate(self.layout[x]):
                d = abs(p_x - x) + abs(p_y - p_y)
                if d >= 2 and d <= 4 and symbol == "*":
                    smelled_pill_distances.add(d)
        # end for
        for d in smelled_pill_distances:
            observation += 2**(d + smell_constant)
        # end for

        # Observe the pellets in sight.
        if len(np.where(layout[p_x, p_y:] == "%")[0]) == 0:
            # right
            if '*' in layout[p_x, p_y:]:
                observation += pacman_sight_observation_enum.sRight

        elif '*' in layout[p_x, p_y:p_y + np.where(layout[p_x, p_y:] == "%")[0][0]]:
            # right
            observation += pacman_sight_observation_enum.sRight

        if len(np.where(layout[p_x, :p_y] == "%")[0]) == 0:
            # left
            if '*' in layout[p_x, :p_y]:
                observation += pacman_sight_observation_enum.sLeft

        elif '*' in layout[p_x, np.where(layout[p_x, :p_y] == "%")[0][-1]:p_y]:
            # left
            observation += pacman_sight_observation_enum.sLeft

        if '*' in layout[np.where(layout[:p_x, p_y] == "%")[0][-1]:p_x, p_y]:
            # down
            observation += pacman_sight_observation_enum.sDown

        if '*' in layout[p_x:np.where(layout[p_x:, p_y] == "%")[0][0], p_y]:
            # top
            observation += pacman_sight_observation_enum.sTop

        # Observe the power pill effect.
        if self.super_pacman:
            observation += pacman_power_observation_enum.underEffect

        return observation

    def move_ghost(self):
        ''' Moves each of the ghosts thus:
              If the Manhattan distance between it and Pacman is <= 5, then
                If Pacman is super, then maximize Manhattan distance.
                Else, minimize.
              Else, move randomly.
              Never move onto another ghost or wall. If it has no where to move,
              then stay in place.
        '''
        p_x, p_y = self.pacman # Pacman location

        for name, position in self.ghost.items(): # Iterate over each ghost.
            x, y = position

            # List of other ghosts. This ghost must not move onto them.
            coordinates = list(self.ghost.values())
            coordinates.remove([x, y])

            # Manhattan distance between Pacman and the current ghost
            old_distance = abs(p_x - x) + abs(p_y - y)

            if old_distance > 5: # Too far from Pacman. Move randomly.
                # Randomly decide to move one step, or not move.
                while True:
                    # Select random displacement
                    dx, dy = random.choice(direction_list + [[0, 0]])
                    new_x = x + dx
                    new_y = y + dy
                    if (new_x, new_y) in self.magic_channel:
                        new_x, new_y = self.magic_channel[new_x, new_y]

                    if self.layout[new_x][new_y] != "%" and [new_x, new_y] not in coordinates:
                        break

            else: # The ghost moves purposefully when close to Pacman.
                # When Pacman is under the effect of power pill, ghosts move
                # every 2 steps by skipping even turns.
                if self.super_pacman and self.super_pacman_time % 2 == 0:
                    continue

                # Try all non-stationary ghost movements.
                decided_flag = False
                for dx, dy in direction_list:
                    new_x, new_y = x + dx, y + dy
                    if (new_x, new_y) in self.magic_channel:
                        new_x, new_y = self.magic_channel[new_x, new_y]

                    # Check if the new location is already occupied.
                    if self.layout[new_x][new_y] == "%" or [new_x, new_y] in coordinates:
                        continue # Occupied. Skip it.

                    # Unoccupied. Check if the new location is more favorable.
                    new_distance = abs(p_x - new_x) + abs(p_y - new_y)
                    if new_distance > old_distance and self.super_pacman or \
                       new_distance < old_distance and not self.super_pacman:
                       # Getting away from super Pacman, or
                       # getting closer to normal Pacman.
                       decided_flag = True
                       break

                # If no good movement has been found, don't move.
                if not decided_flag:
                    new_x, new_y = x, y

            # Move to new location
            self.ghost[name] = [new_x, new_y]

    def print(self):
        """ Returns a string indicating the status of the environment.
        """

        print("=" * 40)
        print(f"Reward: {self.reward}")
        print(f"Super Pacman time remaining: {self.super_pacman_time}")
        print(f"Observation: {self.observation}")
        print(f"Pellets remaining: {self.pellets_remaining}")
        print(self)

    def __str__(self):
        ''' The string reprentation for the class.
        '''

        from copy import deepcopy
        print_map = deepcopy(self.layout)

        for name, value in self.ghost.items():
            x, y = value
            print_map[x][y] = name

        for pill in self.power_pill:
            x, y = pill
            print_map[x][y] = "S"

        x, y = self.pacman
        print_map[x][y] = "P"

        output = ""
        for line in print_map:
            output += "".join(line) + "\n"
        return output

    def running(self):
        '''  Not used by agent.
             Designed for debugging purpose.

             a = Pacman()
             a.running()

             Then we can have the actual interactive with the game


        Parameters
        ----------
        None

        Returns
        -------
        None

        '''

        while not self.is_finished:

            print(self)
            print("==" * 20)
            print(f"Reward :{self.reward}")
            print(f"Super Pacman remainng time {self.super_pacman_time}")
            print(f"Observation : {self.observation}")
            print(f"Pellets remaining :{self.pellets_remaining}")

            action = input("Action is :  ")

            if action == "w":

                action = "1"  # down

            elif action == "s":

                action = "0"  # top

            elif action == "a":

                action = "2"  # left

            else:

                action = "3"  # right

            self.perform_action(action)

        print("**" * 20)
        print('{:^40}'.format("Game Over"))
        print("**" * 20)
