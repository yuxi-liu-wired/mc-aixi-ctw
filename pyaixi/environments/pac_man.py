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

#specify the map of pacman, and the probability to generate the pellets
default_probability = 0.5
layout_txt = "pacMan.txt"

#Define the enumerations to represents the observations and actions
pacman_action_enum = util.enum('top', 'down', 'left', 'right')
pacman_wall_observations_enum = util.enum(wNull = 0, wTopWall = 1,wDownWall = 2,
                                                 wLeftWall = 4, wRightWall = 8)
pacman_ghost_observation_enum = util.enum(gNull = 0, gTopWall = 16,gDownWall = 32,
                                                 gLeftWall = 64, gRightWall = 128)
        
pacman_smell_observation_enum = util.enum(mD_n = 0, mD_2 = 256, mD_3 = 512, mD_4 = 1024)
smell_constant = 4
pacman_sight_observation_enum = util.enum(sNull = 0, sTop = 2048, sDown = 4096, 
                                                  sLeft = 8192, sRight = 16384)
pacman_power_observation_enum = util.enum(withouEffect = 0, underEffect = 32768)

#Predefined dictionary to help us perform the actions 
direction = {
        '0':[1,0], #top
        '1':[-1,0], #down
        '2':[0,-1], # left
        '3':[0,1] #right
              }

direction_list = [[1,0],[-1,0],[0,-1],[0,1]]



class PacMan(environment.Environment):
        
    ''' Pacman

            For the user defined layout, the rules must be followed
            P stands for pacman
            the rest of alphabeta stands for monster
            % stands for wall
            (x,y) - (x_1,y_1) denotes the equivalence of two location. Typlically composed by one invalid location
            and one valid locations.
            
        Attributes
        ----------
        
        rows : int, default 0
            denotes the number of rows in the layout
        
        cols : int, default 0
            denotes the number of columns in the layout
               
        magic_channel : dict()
            used to store the two equivalent locations, typically composed by one invalid location (x,y),
            and one valid loation x_1,y_1,such as 
            magic_channel[x,y] = [x_1,y_1]
               
        max_rewards : int
            denotes the maximum number of rewards the agent could earn
               
        pellets_remaining : int, default 0
            denotes the number of pellets remain on the map
               
        max_observation : int, default 2**16.
            deonotes the largest obersvation value
                
        layout : [[]]
            denotes the game map
                
        monster : dict()
            used to store the current location of monster.
            The key is name of monster, and the value is location of monster
        
        power_pill : []
            used to store the location of remaining power pill on the map.
                
        pacman : [a,b]  a,b belongs to N
            used to store the current location of pacman
                
        reward : int, default 0
            denotes the number the number of scores that our agent has been earned. The minimum
            value will be 0    
            
        is_finished : bool, default False
            used to denote whether the enviroments is finished or not.
            
        super_pacman : bool, default False
            used to denote whether the pacman is under the effect of power pill.
            
        super_pacman_time: int, default 0
            used to denote the remaining time under the effect of power pill.
            
        valid_rewards : range
            used to store the valid rewards
        
        valid_actions: []
            used to store all valid actions
            
        valid_observations: range
            used to store the potential valid observations
            
        observations : int
            the code for current obervations of pacman
            
        actions: int
            the code for action the pacman just taken.
            
        
    '''
    
    
    def __init__(self,options = {}): 
        
        '''
            initialize the setup for our pacman
        
        '''
        
        self.restart()
        
        self.valid_rewards = range(self.max_reward)
        self.valid_actions = list(pacman_action_enum.keys())
        self.valid_observations = range(self.max_observation)
        
        self.action = None
        
     
    def random_pellets(self,x):
        
        
        """ generate pellet according to the defualt probability
            if the current location is not wall ("%"), then there has
            certain chance to having a pellet.
       
        Parameters
        ----------
        x : string
            the symbol of a location on map.
      
        Returns
        -------
        string  "*" or x
            "*" denote the pellet
        
        """        
        
        if x == ' ' and default_probability > random.random():
            
            self.max_reward += 1
            
            return "*"
        
        else:
            
            return x
        
    def load(self,layout):
        
        """ 
            loading the user defined layout of map, and 
            generate the pellets. And setting the number of 
            rows and columns to the attribute
       
        Parameters
        ----------
        layout : string
            the name of file that contains the map
      
        Returns
        -------
        pacMan_map : [[]]
            the list of list representation of the map 
        
        """          
        
        pacMan_map = []
        sep = '/' if '/' in PROJECT_ROOT else ''''\''''
        import inspect
        
        #the path reading is based on the notes on stackoverflow
        #link: https://stackoverflow.com/questions/50499/how-do-i-get-the-path-and-name-of-the-file-that-is-currently-executing
        
        path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) + sep + layout
            
        with open(path) as f:
            lines = f.readlines()
            for line in lines:
                if "!" in line:
                    a,b = line.strip().split("!")
                    a = eval(a)
                    b = eval(b)
                    self.magic_channel[a] = b
                    continue
                    
                line = list(map(self.random_pellets,line))
                line.remove("\n")
                self.pellets_remaining += line.count("*")
                pacMan_map.append(line) 
        
        self.rows = len(pacMan_map)
        self.cols = len(pacMan_map[0])
        return pacMan_map
    
    
    def find_Positions(self):
        
        """ 
            collecting the location information of 
            monster and power pill, and preprocessing the
            map. In order to, only keep the walls and
            pellet on the concrete reprensentation of map.
            For the sake of performing action and movement
            of monster.
            
            Also, calculating the maximum rewards.
       
        Parameters
        ----------
        None
      
        Returns
        -------
        None
        
        """     
        
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
            
        self.max_reward = self.max_reward * 10 + len(self.power_pill) * 100 * 30 + 100
        
        
    def restart(self):
        '''
        restart the enviroment
        
        '''
        self.rows = 0
        self.cols = 0
        self.magic_channel = dict()
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
        self.observation = self.calculate_observation()
                    
            
                          
    def perform_action(self, action):

        """ 
            Perform the actions to pacman. Then, update the map,update the rewards 
            and obersvations accordingly.
            we also perform the movement of monster.
            The caculation of rewards follow the rules below,
                1.The agent receives a penalty of 1 for each movement action
                2.a penalty of 10 for running into a wall, and agenet will stay
                  on the original position
                3.a reward of 10 for each food pellet eaten
                4.a penalty of 50 if it is caught by a ghost
                5.a reward of 100 for collecting all the food
                6.a reward of 10 for eating power pill.
                7.eating a ghost while on a power pill effect gives a reward of 30,
                  also reset the position of ghost
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
        
        self.movement_monster()
        
        self.action = action
        
        self.reward -= 1
                
        # calculate the postion of pacman based  on current location
        # and action
        movement = direction[str(action)]
        
        old_x,old_y = self.pacman
        self.layout[old_x][old_y] = " "
        
        self.pacman = [self.pacman[0] + movement[0],self.pacman[1] + movement[1]]
        
        x,y = self.pacman
        
        #check if the pacman are transposed through magic channel
        if (x,y) in self.magic_channel:
            self.pacman = self.magic_channel[x,y]
            x,y = self.pacman
        on_map = self.layout[x][y]
        
        if on_map == "*":
            
            self.reward += 10
            self.layout[x][y] = " "
            self.pellets_remaining -= 1
        
        elif on_map == "%":
            
            self.reward -= 10
            # if packman is going into the wall
            # keep the old location
            self.pacman = [old_x,old_y]
            x,y = self.pacman
            
        
            
        if [x,y] in self.monster.values():
            
            if self.super_pacman:
                
                # if the monster is eaten by the pacman
                # reset it is location by generate random number
                # also, no monster are in the same location
                
                self.reward += 30
                
                #find out the monster eaten by the pacman
                for name, location in self.monster.items():
                    
                    if location == [x,y]:
                        
                        break
                
                m_x = 0 
                
                m_y = 0
                
                while self.layout[m_x][m_y] == "%" and [m_x,m_y] not in self.monster.values():
                
                    m_x = random.randint(0,self.rows-1)
                    m_y = random.randint(0,self.cols-1)
                    
                self.monster[name] =[m_x,m_y]
                
            else:
                
                self.reward -= 50
                past_reward = max(0,self.reward)
                self.restart()
                return past_reward, self.observation
                
        if on_map == "S":
                
            self.reward+=10
            self.super_pacman = True
            self.super_pacman_time += 100
            self.layout[x][y] = " "
            self.power_pill.remove([x,y])
            
                                                                        
        if self.super_pacman_time > 0:
            
            self.super_pacman_time-=1
            
        if self.super_pacman_time == 0:
            
            self.super_pacman = False
            
        if self.pellets_remaining == 0:
            self.reward += 100
            
        self.reward = max(self.reward,0)
        
        
        # if all pellets are eaten
        # then we restart the game automatically
        if self.pellets_remaining == 0 :
            
            past_reward = self.reward 
            self.restart()        
            return past_reward, self.observation

        #calculate the obervations
        self.observation = self.calculate_observation()
        
        
        return self.reward, self.observation
    
    def calculate_observation(self):
        
        '''
        The observations are calculate according to the rules blow
        
            1.only receives a 4-bit observation describing the wall configuration at 
            its current location.
        
            2.only 4-bit observations indicating whether a ghost is visible (via direct line of sight) 
            in each of the four cardinal directions. 
        
            3.In addition, the location of the food pellets is unknown except for a 3-bit observation that
            indicates whether food can be smelt within a Manhattan distance of 2, 3 or 4 
            from PacMan’s location, 
        
            4. another 4-bit observation indicating whether there is food in its direct line of sight. 
        
            5. final single bit indicates whether PacMan is under the effects of a power pill.
            
        Then we can calculate the oberserbations using the enumerations we defined before
        
        Parameters
        ----------
        None
        
        Returns
        -------
        None
        
        '''
                
        observation = 0
        
        p_x, p_y = self.pacman
        
        # using numpy arrarys are benefits in different ways 
        # of indexing
        layout = np.array(self.layout)
        shadow_layout = np.array(self.layout)
        
        
        #calculate the obervations for wall
        for key,l in direction.items():
            x,y = l
            new_x,new_y = p_x+x,p_y+y
            
            if (new_x,new_y) in self.magic_channel:
                
                new_x,new_y = self.magic_channel[new_x,new_y]
            
            if self.layout[new_x][new_y] == "%":
                # the relation of them 2**?, because of the the mathmatical
                # coincidence
                observation += 2**(int(key))
                
        #calculate the obervations for monster    
        
        for name,l in self.monster.items():
            x,y = l
            shadow_layout[x,y] = name
          
        
        if self.monster_names.intersection(shadow_layout[p_x,p_y:]):
            #right,including at same position
            for name in self.monster_names.intersection(shadow_layout[p_x,p_y:]):
                m_x,m_y = self.monster[name]
                #no wall in the sight
                if "%" not in shadow_layout[p_x,p_y:m_y]:
                    observation+= pacman_ghost_observation_enum.gRightWall
                    break
        
        if self.monster_names.intersection(shadow_layout[p_x,:p_y]):
            #left
            
            for name in self.monster_names.intersection(shadow_layout[p_x,:p_y]):
                m_x,m_y = self.monster[name]
                #no wall in the sight
                if "%" not in shadow_layout[p_x,m_y:p_y]:
                    observation+= pacman_ghost_observation_enum.gLeftWall
                    break
        
        if self.monster_names.intersection(shadow_layout[:p_x,p_y]):
            #down
            for name in self.monster_names.intersection(shadow_layout[:p_x,p_y]):
                m_x,m_y = self.monster[name]
                #no wall in the sight
                if "%" not in shadow_layout[m_x:p_x,p_y]:
                    observation+= pacman_ghost_observation_enum.gDownWall
                    break
            
        if self.monster_names.intersection(shadow_layout[p_x+1:,p_y]):
            #top
            for name in self.monster_names.intersection(shadow_layout[p_x+1:,p_y]):
                m_x,m_y = self.monster[name]
                #no wall in the sight
                if "%" not in shadow_layout[p_x+1:m_x,p_y]:
                    observation+= pacman_ghost_observation_enum.gTopWall
                    break
        
        #calculate the observations for pellets in smelling.        
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
            
        #calculate the observations for pellets in sight.
        
        
        if len(np.where(layout[p_x,p_y:]=="%")[0]) == 0:
            #right
            if '*' in layout[p_x,p_y:]:
                observation+= pacman_sight_observation_enum.sRight
        
        elif '*' in layout[p_x,p_y :p_y+np.where(layout[p_x,p_y:]=="%")[0][0]]:
            #right
            observation+= pacman_sight_observation_enum.sRight
            
        
        if len(np.where(layout[p_x,:p_y]=="%")[0]) == 0:
            #left
            if '*' in layout[p_x,:p_y]:
                observation+= pacman_sight_observation_enum.sLeft
        
        elif '*' in layout[p_x, np.where(layout[p_x,:p_y]=="%")[0][-1]:p_y]:
            #left
            observation+= pacman_sight_observation_enum.sLeft
            
            
        if '*' in layout[np.where(layout[:p_x,p_y]=="%")[0][-1]:p_x,p_y]:
            #down
            observation+= pacman_sight_observation_enum.sDown
        
        if '*' in layout[p_x:np.where(layout[p_x:,p_y]=="%")[0][0],p_y]:
            #top
            observation+= pacman_sight_observation_enum.sTop
        
        #calculate the observations of power pill effect.
        if self.super_pacman:
            
            observation += pacman_power_observation_enum.underEffect
            
        return observation
                    
                
            
        
        
    def movement_monster(self):
        
        ''' Perform the monster movements. And
            the movements of monsters follow the rules below
                1.They move initially at random, until there is a Manhattan 
                distance of 5 between them and PacMan
                
                2. No pairs of monster could stay in the same location
        
        Parameters
        ----------
        None

        Returns
        -------
        None        
        
        '''
        
        p_x,p_y = self.pacman
        
        for name,position in self.monster.items():
            
            x,y = position
            
            # calculate the Manhattan distance between pacman and the current monster
            distance = abs(p_x - x) + abs(p_y - y)
            
            if  distance > 5:
                
                new_x = 0
                new_y = 0
                
                coordinates = list(self.monster.values())
                coordinates.remove([x,y])
                
                #can not move the locations of other monster
                while self.layout[new_x][new_y] == "%" and [new_x,new_y] not in coordinates:
                    
                    # perform random actions
                    # also, the monster has certain chance 
                    # that stay in the orginal 
                    # postion
                    
                    index = random.choices(range(5))[0]
                    
                    if index == 4:
                        new_x = x
                        new_y = y
                    else:
                        m_x,m_y = direction_list[index]
                        new_x = x+m_x
                        new_y = y+m_y
                    
                    if (new_x,new_y) in self.magic_channel:
            
                        new_x,new_y = self.magic_channel[new_x,new_y]
                
                
                self.monster[name] = [new_x,new_y]
                
            else:
                
                # move towards the pacman
                
                valid_actions = []
                
                #consider all of the possible movements
                for m_x,m_y in direction_list:
                    
                    new_x = x+m_x
                    new_y = y+m_y
                    
                    if (new_x,new_y) in self.magic_channel:
            
                        new_x,new_y = self.magic_channel[new_x,new_y]
                        
                    coordinates = list(self.monster.values())
                    coordinates.remove([x,y])
                    
                    if self.layout[new_x][new_y] != "%"  and [new_x,new_y] not in coordinates:
                        
                        valid_actions.append([[new_x,new_y],abs(p_x - new_x) + abs(p_y - new_y)])
                        
                        
                # if no movement is avalible
                # stay in the orginal postion
                if valid_actions == []:
                    
                    continue
                
                # when the pacman is under the power pill,
                # monster move as far as possible.
                # If it is not,
                # the monster move as close as possible.
                
                fun = max if self.super_pacman else min
                
                self.monster[name] = fun(valid_actions,key = lambda x : x[1])[0]
    
    def print(self):
        
        ''' print the interface 
        
        
        Parameters
        ----------
        None

        Returns
        -------
        None    
        
        '''
        
        print("==" * 20)
        print(f"Reward :{self.reward}")
        print(f"Super Pacman remainng time {self.super_pacman_time}")
        print(f"Observation : {self.observation}")
        print(f"Pellets remaining :{self.pellets_remaining}")
        print(self)
             
                
    def __str__(self):
        
        ''' the string reprentation for the class.
        
        
        Parameters
        ----------
        None

        Returns
        -------
        None    
        
        '''        
        
        
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
            
                action = "1" #down
                
            elif action == "s":
            
                action  = "0" #top
                
            elif action == "a":
            
                action = "2" #left
                
            else:
                    
                action = "3" #right
                    
            self.perform_action(action)
            
            
        print("**"*20)
        print('{:^40}'.format("Game Over"))
        print("**"*20)          
                
                        
                    
                    
                    
                    
                    
                
                
            
            
            
        
            
                
                
                    
    
    
    
        