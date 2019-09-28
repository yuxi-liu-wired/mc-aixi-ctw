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

mouse_action_list = util.enum('up','down','left','right')
#                                       5      7      8      9     10     12
mouse_valid_observations = util.enum('5','7','8','9','10','12')

direction = {
        '0':[1,0], #up
        '1':[-1,0], #down
        '2':[0,-1], # left
        '3':[0,1] #right
              }


def readMazeFile():
	maze = []
	f = open("cheeseMaze.txt","r")
	row = 0;
	for line in f.readlines():
		maze.append(line[:-1].split(','))

	for row in maze:
		for col in row:
			if col == '1':
				print('*', end = '')
			else:
				print(' ', end = '')
		print()
	return maze


class CheeseMaze(environment.Environment):

	def __init__(self, options = {}):
		environment.Environment.__init__(self, options = options)
		self.maze = readMazeFile()
		self.mouse = (1,1)
		self.cheese = (3,3)
		self.valid_rewards = range(2**5)
		self.valid_actions = list(mouse_action_list.keys())


	def perform_action(self, action):
		""" Receives the agent's action and calculates the new environment percept.
		"""

		assert self.is_valid_action(action)
		self.action = action
		self.move(action)

	def move(self, action):
		assert self.is_valid_action(action)
		movement = direction[str(action)]
		if(maze[self.mouse[0]+movement[0]][self.mouse[1]+movement[1]] == '1'):
			self.reward -= 10
		else:
			self.mouse = (self.mouse[0]+movement[0], self.mouse[1]+movement[1])
			self.reward -= 1
			if self.check_game_over():
				self.reward += 10
		self.observation = maze[self.mouse[0]][self.mouse[1]]

	def check_game_over(self):
		if self.mouse[0] == self.cheese[0] and self.mouse[1] == self.cheese[1]:
			self.is_finished = True
		return True

    
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









