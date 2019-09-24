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

from pyaixi import environment, util

default_probability = 0.5
layout_txt = "pacMan.txt"
pacman_action_enum = util.enum('top', 'down', 'left', 'right')

direction = {
        'top':[1,0],
        'down':[-1,0],
        'left':[0,-1],
        'right':[0,1]
              }

direction_list = [[1,0],[-1,0],[0,-1],[0,1]]

class PacMan(environment.Environment):
    
    
    def __init__(self):
        
        '''
        P stands for pacman
        the rest of alphabeta stands for monster
        % stands for wall
        * stands for pellets
        
        '''
        
        self.layout = self.load(layout_txt)
        self.rows = 0
        self.cols = 0
        self.monster = dict()
        self.power_pill = []
        self.pacman = None
        self.find_Positions()
        self.reward = 0
        self.isalive = True
        self.super_pacman = False
        self.super_pacman_time = 0
     
    def random_pellets(self,x):
        
        if x == ' ' and default_probability > random.random():
            
            return "*"
        
        else:
            return x
        
    def load(self,layout):
        pacMan_map = []
        
        with open(layout) as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                line = map(self.random_pellets,line)
                pacMan_map.append(list(line)) 
        
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
                          
    def perform_action(self, action):
        
        
        self.reward -= 1
        
        movement = direction[action]
        
        self.pacman = [self.pacman[0] + movement[0],self.pacman[1] + movement[1]]
        
        x,y = self.pacman
        
        on_map = self.layout[x][y]
        
        if on_map == "*":
            
            self.reward += 10
            self.layout[x][y] = " "
        
        elif on_map == "%":
            
            self.reward -= 10
            
            self.isalive = False
            
        elif on_map.isalpha():
            
            if self.super_pacman:
                
                self.reward += 30
                
                name = self.monster[on_map]
                
                m_x = 0 
                
                m_y = 0
            
                while self.layout[m_x][m_y] == "%":
                    
                    m_x = random.randint(0,self.rows-1)
                    m_y = random.randint(0,self.cols-1)
                    
                self.monster[name] ==[m_x,m_y]
                
            else:
                
                self.reward -= 10
            
                self.isalive = False
            
        elif on_map == "S":
            
            self.reward+=10
            self.super_pacman = True
            self.super_pacman_time = 100
            self.layout[x][y] = " "
            
            
        if self.super_pacman_time > 0:
            
            self.super_pacman_time-=1
            
        if self.super_pacman_time == 0:
            
            self.super_pacman = False
            
        
    def movement_monster(self):
        
        p_x,p_y = self.pacman
        
        for name,position in self.monster.items():
            
            x,y = position
            
            distance = abs(p_x - x) + abs(p_y - y)
            
            if  distance > 5:
                
                new_x = 0
                new_y = 0
                
                while self.layout[new_x][new_y] == "%":
                    
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
                    
                    if self.layout[new_x][new_y] != "%":
                        
                        valid_actions.append([[new_x,new_y],abs(p_x - new_x) + abs(p_y - new_y)])
                
                fun = max if self.super_pacman else min
                self.monster[name] = fun(valid_actions,key = lambda x : x[1])[0]
    
             
                
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
            
            
        while self.isalive:
                
            print(self)
            print("==" * 20)
            print(f"Reward :{self.reward}")
            
            action = input()
            
            if action == "w":
            
                action = "top"
                
            elif action == "s":
            
                action  = "down"
                
            elif action == "a":
            
                action = "left"
                
            else:
                    
                action = "right"
                    
            self.perform_action(action)
            self.movement_monster()
                    
                
                        
                    
                    
                    
                    
                    
                
                
            
            
            
        
            
                
                
                    
    
    
    
        