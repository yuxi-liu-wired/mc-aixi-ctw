#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 21 15:18:40 2019

@author: Yan
"""

from ctw_context_tree import CTWContextTree, CTWContextTreeNode
import unittest
import random
from collections import Counter
import math
from copy import deepcopy

def log_kt(random_string):
    (_,a),(_,b) = Counter(random_string).most_common()
    return calculate_log_kt(a,b)

def calculate_log_kt(a,b):
    
    if a==0 and b==0:
        return math.log(1)
    elif a > 0:
        return math.log((a - 1 + 0.5) / (a-1+b+1)) + calculate_log_kt(a-1,b)
    else:
        return math.log((b - 1 + 0.5 )/ (a + b - 1 + 1)) + calculate_log_kt(a,b-1)
    
    
def random_Binarystring():
    result = random.randint(0, 10000)
    random_string = bin(result)[2:]
    return random_string

def feed_ctwnode(string,node):
    for bit in string:
        node.update(bit)
    return node

def revert_ctwnode(string,node):
    for bit in string:
        node.revert(bit)
    return node

def check_fieldvalue(node1,node2):
    
    field_1 = node1.__dict__
    field_2 = node2.__dict__
    
    correct = 0
    for key,value in field_1.items():
        
        value_2 = field_2[key]
        
        if isinstance(value,float):
            
            if abs(value - value_2) < 1e-6:
                correct+=1
        else:
            
            if value == value_2:
                correct+=1
    return correct/len(field_1)
    

class TestCTWContextTreeNode(unittest.TestCase):
    
    #Simplying consider the number of 1s and 0s in the random string
    #To check if the function is functional correct
    # Test update
    def test_log_kt_multiplier(self):
        node = CTWContextTreeNode()
        
        #random string 
        random_string = random_Binarystring()
        node = feed_ctwnode(random_string,node)
            
        result = log_kt(random_string)
        self.assertAlmostEqual(result,node.log_kt,7,"log_kt tests")
        
    
    def test_update_revert_case_1(self):
        '''
        fill the node and then empty the node
        '''
        node = CTWContextTreeNode()
        original_node = deepcopy(node)
        #random string 
        random_string = random_Binarystring()
        node = feed_ctwnode(random_string,node)
        node = revert_ctwnode(random_string,node)
        
        self.assertEqual(check_fieldvalue(original_node,node),1,"revert test")
        
        
    def test_update_revert_case_2(self):
        
        '''
        consider the node that already been feeded
        '''
        node = CTWContextTreeNode()
        #random string 
        random_string_1 = random_Binarystring()
        node = feed_ctwnode(random_string_1,node)
        
        original_node = deepcopy(node)
        random_string_2 = random_Binarystring()
        node = feed_ctwnode(random_string_2,node)
        node = revert_ctwnode(random_string_2,node)
        
        self.assertEqual(check_fieldvalue(original_node,node),1,"revert test")
   
def count_context(past,sequence,context,a):
    
    '''
    Tree  T = {00,10,1}
    
    Contexts T 01001100 with past...110:
    
    1  1  0 |  0  1  0  0  θ  1  1  0  1  1  0
            |    00          00
    past    | 10        10
            |        1                    1  1
            
    Examples retrieved from Context Tree Weighting -- Peter Sunehag and Marcus Hutter
    '''
    
    if len(past) < len(a):
        string = past + sequence
    else:
        past = past[-len(a):]
        string = past + sequence
    
    count = 0

    l = len(context)
    
    if l >= len(string):
        return count 
    
    current_bit = string[:l]
    
    for bit in string[l:]:
        
        if current_bit == context and bit == a:
            count+=1
        
        current_bit = current_bit[1:] + bit
            
    return count
    
    

class TestCTWContextTree(unittest.TestCase):
    
    def test_update(self):
        tree = CTWContextTree(3)
        tree.update("110")
        tree.update("0100110")
        symbol_count = tree.root.children[0].children[1].symbol_count
        a = symbol_count[0]
        b = symbol_count[1]
        ground_truth_a = count_context("110","01001100","10","0")
        ground_truth_b = count_context("110","01001100","10","1")
        self.assertEqual(a,ground_truth_a,"incorrect update")
        self.assertEqual(b,ground_truth_b,"incorrect update")
        
    def test_predict(self):
        tree = CTWContextTree(3)
        tree.update("110")
        p = tree.predict("0100110")  
        self.assertAlmostEqual(7/2048,p,8,"prediction wrong")
        
    def test_generate_random_action(self):
        tree = CTWContextTree(3)
        tree.update("110")
        tree.update("0100110")  
        
        action = [[0,1,1,1],[0,1,0,1]]
        
        t = True
        
        for epoch in range(10):
           t = t and (tree.generate_random_actions(action) in action)
        
        assert t, "invalid random actions"
        
        
    def test_model_revert(self):
        tree = CTWContextTree(3)
        tree.set_tade_off(True)
        tree.update("110")
        past_ctw =deepcopy(tree)
        p = tree.predict("0100110")  
        
        assert check_fieldvalue(past_ctw,tree), "invalid reverting"
        
        

if __name__ == '__main__':
    unittest.main()