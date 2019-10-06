#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import inspect
from pyaixi import environment, util
import os
import random
import sys

# Insert the package's parent directory into the system search path, so that this package can be
# imported when the aixi.py script is run directly from a release archive.
PROJECT_ROOT = os.path.realpath(os.path.join(os.pardir, os.pardir))
sys.path.insert(0, PROJECT_ROOT)


# Defines an enumeration to represent agent action: moving in one of 4 possible directions.
cheese_maze_action_enum = util.enum('up', 'down', 'left', 'right')

# Defines an enumeration to represent agent observation:
# There are six possible observations, numbered in a rather haphazard way.
cheese_maze_observation_enum = util.enum(
    five=5, seven=7, eight=8, nine=9, ten=10, twelve=12)

# Defines an enumeration to represent agent reward:
# bumping into wall: 0
# moving into an empty cell: 9
# getting the cheese: 20
cheese_maze_reward_enum = util.enum(wall=0, move=9, cheese=20)

# Defines some shorthand notation for ease of reference.
up = cheese_maze_action_enum.up
down = cheese_maze_action_enum.down
left = cheese_maze_action_enum.left
right = cheese_maze_action_enum.right

wall = cheese_maze_reward_enum.wall
move = cheese_maze_reward_enum.move
cheese = cheese_maze_reward_enum.cheese

five = cheese_maze_observation_enum.five
seven = cheese_maze_observation_enum.seven
eight = cheese_maze_observation_enum.eight
nine = cheese_maze_observation_enum.nine
ten = cheese_maze_observation_enum.ten
twelve = cheese_maze_observation_enum.twelve

# The actual maze has the shape:
# 1,1,1,1,1,1,1
# 1,9,10,8,10,12,1
# 1,5,1,5,1,5,1
# 1,7,1,7,1,7,1
# 1,1,1,1,1,1,1
# where 1 stands for walls.

# The observed name of each cell in the coordinate system.
location_alias = {(1, 1): nine, (1, 2): ten, (1, 3): eight, (1, 4): ten, (1, 5): twelve,
                 (2, 1): five,              (2, 3): five,               (2, 5): five,
                 (3, 1): seven,             (3, 3): seven,              (3, 5): seven}
direction = {
    '0': [1, 0],  # up
    '1': [-1, 0],  # down
    '2': [0, -1],  # left
    '3': [0, 1]  # right
}

layout_filename = "cheese_maze.txt"
sep = '/' if '/' in PROJECT_ROOT else '\\'
path = os.path.dirname(
        os.path.abspath(
            inspect.getfile(
                inspect.currentframe()))) + sep + layout_filename

"""
%%%%%%%
%     %
% % % %
% % % %
%%%%%%%
"""

# Construct the map.
map = {}
with open(path) as f:
    row = 0
    col = 0

    for line in f:
        for s in list(line.rstrip()):
            if s == "%":
                map[(row, col)] = s
            else:
                map[(row, col)] = location_alias[(row, col)]
            col = ((col + 1) % 7)
        row += 1
print(map)


class CheeseMaze(environment.Environment):

    def __init__(self, options={}):
        environment.Environment.__init__(self, options=options)
        self.maze = map
        self.mouse = util.choice(
            [x for x in map.keys() if map[x] != '%'])
        self.cheese = util.choice(
            [x for x in map.keys() if map[x] != '%'] and x != self.mouse)

        # Defines the acceptable action values.
        self.valid_actions = list(cheese_maze_action_enum.keys())
        # Defines the acceptable observation values.
        self.valid_observations = list(cheese_maze_observation_enum.keys())
        # Defines the acceptable reward values.
        self.valid_rewards = list(cheese_maze_observation_enum.keys())

        self.observation = map[self.mouse]
        self.reward = 0

    def perform_action(self, action):
        """ Receives the agent's action and calculates the new environment percept.

        - `action`: action of the agent
        """

    self.action = action
    y, x = self.mouse
    if action == up:
        y -= 1
    elif action == down:
        y += 1
    elif action == left:
        x -= 1
    else:
        x += 1
    # end if

    if map[y, x] == "%":
        self.reward = wall
    else:
        self.reward = move
        self.observation = map[y, x]
        self.mouse = (y, x)
        if self.cheese == (y, x):
            self.reward += cheese
    # end if

    # return self.observation, self.action

    # Store the observation and reward in the environment.
    self.observation = observation
    self.reward =

    # return (observation, reward)

#    def clear

    def print(self):
        """ Returns a string indicating the status of the environment.
        """

        message = "Action: " + \
            (self.action) + \
            ", observation: " + \
            self.observation + \
            ", reward: %d" % self.reward

        return message


readMazeFile()
