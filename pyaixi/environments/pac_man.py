#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 24 22:20:04 2019

@author: Yan
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import random
import sys
import numpy as np

# Insert the package's parent directory into the system search path, so that this package can be
# imported when the aixi.py script is run directly from a release archive.
PROJECT_ROOT = os.path.realpath(os.path.join(os.pardir, os.pardir))
sys.path.insert(0, PROJECT_ROOT)
from pyaixi import environment, util

default_probability = 0.5
layout_txt = "pacMan.txt"
pacman_action_enum = util.enum('top', 'down', 'left', 'right')
pacman_wall_observations_enum = util.enum(wNull = 0, wTopWall = 1,wDownWall = 2,
                                                 wLeftWall = 4, wRightWall = 8)
pacman_ghost_observation_enum = util.enum(gNull = 0, gTopWall = 16,gDownWall = 32,
                                                 gLeftWall = 64, gRightWall = 128)
        
pacman_smell_observation_enum = util.enum(mD_n = 0, mD_2 = 256, mD_3 = 512, mD_4 = 1024)
smell_constant = 4
pacman_sight_observation_enum = util.enum(sNull = 0, sTop = 2048, oDown = 4096, 
                                                  sLeft = 8192, sRight = 16384)
pacman_power_observation_enum = util.enum(withouEffect = 0, underEffect = 32768)


direction = {
        '0':[1,0], #top
        '1':[-1,0], #down
        '2':[0,-1], # left
        '3':[0,1] #right
              }

direction_list = [[1,0],[-1,0],[0,-1],[0,1]]



class PacMan(environment.Environment):
    
    
    def __init__(self,options = {}):
        
        '''
        P stands for pacman
        the rest of alphabeta stands for monster
        % stands for wall
        * stands for pellets
        
        '''
        self.rows = 0
        self.cols = 0
        self.max_reward = 0
        self.pellets_remaining = 0
        self.max_observation = 2**16
        self.layout = self.load(layout_txt)
        self.monster = dict()
        self.power_pill = []
        self.pacman = None
        self.find_Positions()
        self.reward = 0
        self.monster_names = set(self.monster.keys())
        self.is_finished = False
        self.super_pacman = False
        self.super_pacman_time = 0
        
        self.valid_rewards = range(self.max_reward)
        self.valid_actions = list(pacman_action_enum.keys())
        self.valid_observations = range(self.max_observation)
        
        self.observation = self.calculate_observation()
        self.action = None
        
        self.foragent = True
     
    def random_pellets(self,x):
        
        if x == ' ' and default_probability > random.random():
            
            self.max_reward += 1
            
            return "*"
        
        else:
            
            return x
        
    def load(self,layout):
        
        pacMan_map = []
        
        import os
        cwd = os.getcwd()
        
        if "pyaixi" in cwd:
            tokens = cwd.split("/")
            path   = "/".join(tokens[:tokens.index("pyaixi")]) + f"/pyaixi/environments/{layout}"
         
        elif "pyaixi/environments" not in cwd:
            path = cwd+f"/pyaixi/environments/{layout}"
            
        else:
            path = layout
            
        with open(path) as f:
            lines = f.readlines()
            for line in lines:
                
                line = line.strip()
                line = list(map(self.random_pellets,line))
                self.pellets_remaining += line.count("*")
                pacMan_map.append(line) 
        
        self.rows = len(pacMan_map)
        self.cols = len(pacMan_map[0])
        return pacMan_map
    
    
    def find_Positions(self):
        
        row = 0
        
        for line in self.layout:
            
            col = 0
            
            for char in line:
                
                if char =="P":
                    self.pacman = [row,col]
                    
                elif char == "S":
                    
                    self.power_pill.append([row,col])
                
                elif char.isalpha():
                    
                    self.monster[char] = [row,col]
                    
                
                col+=1
                
            row+=1
            
        for name,positon in self.monster.items():
            
            x,y = positon
            self.layout[x][y] = " "
            
        self.max_reward = self.max_reward * 10 + len(self.power_pill) * 100 * 30
            
                          
    def perform_action(self, action):
        
        if self.foragent:
            self.movement_monster()
        
        self.action = action
        
        self.reward -= 1
        
        if self.pellets_remaining == 0:
            
            self.layout = self.load(layout_txt) 
            
            return self.perform_action(action)
        
        movement = direction[str(action)]
        
        old_x,old_y = self.pacman
        self.layout[old_x][old_y] = " "
        if self.layout[self.pacman[0] + movement[0]][self.pacman[1] + movement[1]] != '%':
            self.pacman = [self.pacman[0] + movement[0],self.pacman[1] + movement[1]]
        
        x,y = self.pacman
        
        on_map = self.layout[x][y]
        
        if on_map == "*":
            
            self.reward += 10
            self.layout[x][y] = " "
        
        elif on_map == "%":
            
            self.reward -= 10
            self.pacman = [old_x,old_y]
            
            
        else:
            
            if [x,y] in self.monster.values():
                            
                if self.super_pacman:
                
                    self.reward += 30
                    
                    for name, location in self.monster:
                        
                        if location == [x,y]:
                            
                            break
                    
                    m_x = 0 
                    
                    m_y = 0
                    
                    while self.layout[m_x][m_y] == "%" and [m_x,m_y] in self.monster.values():
                    
                        m_x = random.randint(0,self.rows-1)
                        m_y = random.randint(0,self.cols-1)
                    
                    self.monster[name] ==[m_x,m_y]
                    
                else:
                    
                    self.reward -= 50
            
            
            elif on_map == "S":
                
                self.reward+=10
                self.super_pacman = True
                self.super_pacman_time += 100
                self.layout[x][y] = " "
                self.power_pill.remove([x,y])
                                                                        
        if self.super_pacman_time > 0:
            
            self.super_pacman_time-=1
            
        if self.super_pacman_time == 0:
            
            self.super_pacman = False
            
        self.reward = max(self.reward,0)
                
        self.observation = self.calculate_observation()
        
        return self.reward, self.observation
    
    def calculate_observation(self):
        
        '''
        only receives a 4-bit observation describing the wall configuration at 
        its current location.
        
        only 4-bit observations indicating whether a ghost is visible (via direct line of sight) 
        in each of the four cardinal directions. 
        
        In addition, the location of the food pellets is unknown except for a 3-bit observation that
        indicates whether food can be smelt within a Manhattan distance of 2, 3 or 4 
        from PacMan’s location, 
        
        and another 4-bit observation indicating whether there is food in its direct line of sight. 
        
        A final single bit indicates whether PacMan is under the effects of a power pill.
        
        '''
                
        observation = 0
        
        p_x, p_y = self.pacman
        
        layout = np.array(self.layout)
        shadow_layout = np.array(self.layout)
        
        for key,l in direction.items():
            x,y = l
            
            if self.layout[p_x+x][p_y+y] == "%":
                
                observation += 2**(int(key))
        
        for name,l in self.monster.items():
            x,y = l
            shadow_layout[x,y] = name
            
        if self.monster_names.intersection(shadow_layout[x,y+1:]):
            #top
            observation+= pacman_ghost_observation_enum.gTopWall
        
        if self.monster_names.intersection(shadow_layout[x,:y]):
            #down
            observation+= pacman_ghost_observation_enum.gDownWall
            
        if self.monster_names.intersection(shadow_layout[:x,y]):
            #left
            observation+= pacman_ghost_observation_enum.gLeftWall
            
        if self.monster_names.intersection(shadow_layout[x+1:,y]):
            #right
            observation+= pacman_ghost_observation_enum.gRightWall
        
                
        distance = [2,3,4]
        
        smelles = set()
        
        for x,line in enumerate(self.layout):
            
            for y,symbol in enumerate(self.layout[x]):
                
                d = abs(p_x - x) + abs(p_y - p_y)
                
                if d in distance and symbol == "*":
                    distance.remove(d)
                    smelles.add(d)
        
        for d in smelles:
            
            observation+=2**(d+smell_constant)
                            
        if '*' in layout[x,y+1:]:
            #top
            observation+= pacman_sight_observation_enum.sTop
        
        if '*' in layout[x,:y]:
            #down
            observation+= pacman_sight_observation_enum.sDown
            
        if '*' in layout[:x,y]:
            #left
            observation+= pacman_sight_observation_enum.sLeft
            
        if '*' in layout[x+1:,y]:
            #right
            observation+= pacman_sight_observation_enum.sRight
            
        if self.super_pacman:
            
            observation += pacman_power_observation_enum.underEffect
            
        return observation
                    
                
            
        
        
    def movement_monster(self):
        
        p_x,p_y = self.pacman
        
        for name,position in self.monster.items():
            
            x,y = position
            
            distance = abs(p_x - x) + abs(p_y - y)
            
            if  distance > 5:
                
                new_x = 0
                new_y = 0
                
                while self.layout[new_x][new_y] == "%" and [new_x,new_y] not in self.monster.values():
                    
                    index = random.choices(range(4))[0]
                    m_x,m_y = direction_list[index]
                    new_x = x+m_x
                    new_y = y+m_y
                
                
                self.monster[name] = [new_x,new_y]
                
            else:
                
                valid_actions = []
                
                for m_x,m_y in direction_list:
                    
                    new_x = x+m_x
                    new_y = y+m_y
                    
                    if self.layout[new_x][new_y] != "%"  and [new_x,new_y] not in self.monster.values():
                        
                        valid_actions.append([[new_x,new_y],abs(p_x - new_x) + abs(p_y - new_y)])
                        
                        
                    
                if valid_actions == []:
                    
                    continue
                        
                fun = max if self.super_pacman else min
                
                self.monster[name] = fun(valid_actions,key = lambda x : x[1])[0]
    
    def print(self):
        print("==" * 20)
        print(f"Reward :{self.reward}")
        print(f"Super Pacman remainng time {self.super_pacman_time}")
        print(f"Observation : {self.observation}")
        print(self)
             
                
    def __str__(self):
        
        from copy import deepcopy   
        
        print_map = deepcopy(self.layout)
        
        for name, value in self.monster.items():
            x , y = value
            print_map[x][y] = name
            
        for pill in self.power_pill:
            
            x,y = pill
            print_map[x][y] = "S"
            
        x,y = self.pacman
        
        print_map[x][y] = "P"
        
        output = ""
        
        for line in print_map:
            
            output+= "".join(line) + "\n"
            
        
        return output
                
    def running(self):
            
            
        while not self.is_finished:
                
            print(self)
            print("==" * 20)
            print(f"Reward :{self.reward}")
            print(f"Super Pacman remainng time {self.super_pacman_time}")
            print(f"Observation : {self.observation}")
            
            action = input("Action is :  ")
            
            if action == "w":
            
                action = "1" #down
                
            elif action == "s":
            
                action  = "0" #top
                
            elif action == "a":
            
                action = "2" #left
                
            else:
                    
                action = "3" #right
                    
            self.perform_action(action)
            self.movement_monster()
            
            
        print("**"*20)
        print('{:^40}'.format("Game Over"))
        print("**"*20)          
                
                        
                    
                    
                    
                    
                    
                
                
            
            
            
        
            
                
                
                    
    
    
    
        