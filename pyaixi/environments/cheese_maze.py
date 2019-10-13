#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import sys

# Insert the package's parent directory into the system search path, so that this package can be
# imported when the aixi.py script is run directly from a release archive.
PROJECT_ROOT = os.path.realpath(os.path.join(os.pardir, os.pardir))
sys.path.insert(0, PROJECT_ROOT)

from pyaixi import environment, util

# Defines an enumeration to represent agent action: move up, down, left, right in the maze
cheese_maze_action_enum = util.enum('up', 'down', 'left', 'right')

# Defines an enumeration to represent agent observation: which aliased location the mouse is at
cheese_maze_observation_enum = util.enum(five = 5, seven = 7, eight = 8, nine = 9, ten = 10, twelve = 12)

# Defines an enumeration to represent agent reward: the agent took an invalid step or valid or highest rewarded step
cheese_maze_reward_enum = util.enum(wall = 0, move = 9, cheese = 20)

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

alias_setting = {(1,1):nine, (1,2):ten, (1,3):eight, (1,4):ten, (1,5):twelve
                 ,(2,1):five, (2,3):five, (2,5):five, (3,1):seven, (3,3):seven, (3,5):seven}
# read maze file
layout = "cheese_maze.txt"
sep = '/' if '/' in PROJECT_ROOT else ''''\''''
import inspect
path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) + sep + layout

# Setting up coordinates for maze
coordinator = {}

with open(path) as f:
    row = 0
    col = 0

    for line in f:
        for s in list(line.rstrip()):
            if s == "%":
                coordinator[(row,col)] = s
            else:
                coordinator[(row,col)] = alias_setting[(row,col)]
            col=((col+1)%7)
        row+=1
        
class CheeseMaze(environment.Environment):
    """ A mouse and a cheese are in the same two-dimensional 7x5 maze. The task
        is to get the cheese by taking least actions. 
        
        Action: Agent has only 4 choice of actions: moving up, down, left, right
        in maze.
        
        Observations: each free cell has a location observation with decimal 
        number([5,7,8,9,10,12]), and multiple locations may share one observa-
        tion. The problem exhibits perceptual aliasing in that a single observ-
        ation is potentially ambiguous.
        
        
        Reward: Agent receive a penalty reward of 0 if it move towards a cell
        occupied by wall(%), it receive a moving(9) reward by moving into
        a free cell, it get the highest acceptable reward(30) if it moves into a 
        location contains cheese.
    """
    
    def __init__(self, options = {}):
        # Set up the base environment.
        environment.Environment.__init__(self, options = options)
        self.maze = coordinator # maze contains dcitionary of the environment

        self.cheese = (3,3) # permanent address of cheese
        
        # Defines the acceptable action values.
        self.valid_actions = list(cheese_maze_action_enum.keys())

        # Defines the acceptable observation values.
        self.valid_observations = list(cheese_maze_observation_enum.keys())

        # Defines the acceptable reward values.
        self.valid_rewards = list(cheese_maze_observation_enum.keys())

        # Initiate the game
        self.clear_restart()
        self.reward = 0

    def perform_action(self, action):
        """ Receives the agent's action and calculates the new environment percept.
        """
        assert self.is_valid_action(action)
        
        # save the action
        self.action = action
        
        # read coordinates of mouse
        y,x = self.mouse
        
        
        # movement effect of different direction
        if action == up:
            y -= 1
        elif action == down:
            y += 1
        elif action == left:
            x -= 1
        else:
            x += 1
            
        # agent bumps into a wall
        if self.maze[y,x] == "%":
#            print('hit wall')
            self.reward = wall # penalty reward for bumping into wall
        else:
            self.mouse = (y,x) # update agent coordinate
            self.observation = self.maze[self.mouse]
            self.reward = move # reward for a valid movement
            if self.cheese == (y,x): # agent found the cheese
#                print("YOU GOT CHEESE!!!!")
                self.reward += cheese # adding cheese reward to self.reward result in max(reward) = 29 (5 bit)
                self.clear_restart() # restart the game by resetting agent location and observation
#                print(self.mouse)
        return self.observation, self.reward

    def clear_restart(self):
        self.mouse = (1,2) # initial position for agent
        self.observation = self.maze[self.mouse] # initial observation (agent initial location)
        

#    def print(self):
#        message = "Action: " + str(self.action) + ", observation" + str(self.observation) + ", reward: %d" %self.reward
#        return message






