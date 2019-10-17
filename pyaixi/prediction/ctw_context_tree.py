#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Define classes to implement context trees according to the Context Tree Weighting algorithm.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import math
import random

# Ensure xrange is defined on Python 3.
from six.moves import xrange
from collections import deque
from copy import deepcopy

# The value ln(0.5).
# This value is used often in computations and so is made a constant for efficiency reasons.
log_half = math.log(0.5)

'''
I do not maintain the tree size exactly,
because when the depth get larger.
Calculating the tree size
is horible.

'''

class CTWContextTreeNode:
    """ The CTWContextTreeNode class represents a node in an action-conditional context tree.


        The purpose of each node is to calculate the weighted probability of observing
        a particular bit sequence.

        In particular, denote by `n` the current node, by `n0` and `n1`  the child nodes,
        by `h_n` the subsequence of the history relevant to node `n`, and by `a`
        and `b` the number of zeros and ones in `h_n`.

        Then the weighted block probability of observing `h_n` at node `n` is given by

          P_w^n(h_n) :=
  
            Pr_kt(h_n)                        (if n is a leaf node)
            1/2 Pr_kt(h_n) +
            1/2 P_w^n0(h_n0) P_w^n1(h_n1)     (otherwise)

        where `Pr_kt(h_n) = Pr_kt(a, b)` is the Krichevsky-Trofimov (KT) estimator defined by the relations

          Pr_kt(a + 1, b) = (a + 1/2)/(a + b + 1) Pr_kt(a, b)

          Pr_kt(a, b + 1) = (b + 1/2)/(a + b + 1) Pr_kt(a, b)

        and the base case

          Pr_kt(0, 0) := 1


        In both relations, the fraction is referred to as the update multiplier and corresponds to the
        probability of observing a zero (first relation) or a one (second relation) given we have seen
        `a` zeros and `b` ones.

        Due to numerical issues, the implementation uses logarithmic probabilities
        `log(P_w^n(h_n))` and `log(Pr_kt(h_n)` rather than normal probabilities.

        These probabilities are recalculated during updates (`update()`)
        and reversions (`revert()`) to the context tree that involves the node.

        - The KT estimate is accessed and stored using `log_kt`.
          It is updated from the previous estimate by multiplying with the update multiplier as
          calculated by `log_kt_multiplier()`.

        - The weighted probability is access and stored using `log_probability`.
          It is recalculated by `update_log_probability()`.

        In order to calculate these probabilities, `CTWContextTreeNode` also stores:

        - Links to child nodes: `children`

        - The number of symbols (zeros and ones) in the history subsequence relevant to the
          node: `symbol_count`.


        The `CTWContextTreeNode` class is tightly coupled with the `ContextTree` class.

        Briefly, the `ContextTree` class:

        - Creates and deletes nodes.

        - Tells the appropriate nodes to update/revert their probability estimates.

        - Samples actions and percepts from the probability distribution specified
          by the nodes.
    """

    # Instance methods.

    def __init__(self, tree = None):
        """ Construct a node of the context tree.
        """

        # The children of this node.
        self.children = {}

        # The tree object associated with this node.
        self.tree = tree

        # The cached KT estimate of the block log probability for this node.
        # This value is computed only when the node is changed by the update or revert methods.
        self.log_kt = 0.0

        # The cached weighted log probability for this node.
        # This value is computed only when the node is changed by the update or revert methods.
        self.log_probability = 0.0

        # The count of the symbols in the history subsequence relevant to this node.
        self.symbol_count = {0: 0, 1: 0}
    # end def

    def is_leaf_node(self):
        """ Return True if the node is a leaf node, False otherwise.
        """

        # If this node has no children, it's a leaf node.
        return self.children == {}
    # end def

    def log_kt_multiplier(self, symbol):
        """ Returns the logarithm of the KT-estimator update multiplier.

           The log KT estimate of the conditional probability of observing a zero given
           we have observed `a` zeros and `b` ones at the current node is

             log(Pr_kt(0 | 0^a 1^b)) = log((a + 1/2)/({a + b + 1))

           Similarly, the estimate of the conditional probability of observing a one is

             log(\Pr_kt(1 |0^a 1^b)) = log((b + 1/2)/(a + b + 1))

           - `symbol`: the symbol for which to calculate the log KT estimate of
             conditional probability.

             0 corresponds to calculating `log(Pr_kt(0 | 0^a 1^b)` and
             1 corresponds to calculating `log(Pr_kt(1 | 0^a 1^b)`.
        """

        # TODO: implement
        
        a = self.symbol_count[0]
        
        b = self.symbol_count[1]
        
        #find out which bit is we have based the current symbol counts, 0 or 1.
        numerator  = b if symbol else a
        
        log_Pr_kt = math.log((numerator + 0.5)/(a + b +  1))
        
        return log_Pr_kt
    # end def

    def revert(self, symbol):
        """ Reverts the node to its state immediately prior to the last update.
            This involves updating the symbol counts, recalculating the cached
            probabilities. 

            - `symbol`: the symbol used in the previous update.
        """

        # TODO: implement
        symbol = int(symbol)
        
        
        # remove uneccessary child,
        # otherwise, it will throw the memory error.
        # As during the mcts, we are very likely to create lots
        # of impossible nodes.  (find during experiments)
        # Also, if we donot remove uneccessary chirlds
        # we will get inaccurate probability for each of non-leaf node.
        # because the leaf node is the base case for our recursive appraoch 
        # of calculating probability.
        if symbol in self.children:
            
            child = self.children[symbol]
            
            if sum(child.symbol_count.values()) ==  0:
                
                del self.children[symbol]
                
                
        #consistent with log_kt_multiplier
        
        # the symbol count should be non-negative
        self.symbol_count[symbol]  = max(0, self.symbol_count[symbol]-1)
              
        #calculating the log probability relies on the kt estimater
        #update the kt estimator before updating the log probability   
        self.log_kt -= self.log_kt_multiplier(symbol)
        
        #the probability is depend on the kt estimater, so
        # it should be update at end.
        
        self.update_log_probability()
        
    # end def

    def size(self):
        """ The number of descendants of this node.
        """

        # Iterate over the direct children of this node, collecting the size of each sub-tree.
        return 1 + sum([child.size() for child in self.children.values()])
    # end def
    
    def update(self, symbol):
        """ Updates the node after having observed a new symbol.
            This involves updating the symbol counts and recalculating the cached probabilities.

            - `symbol`: the symbol that was observed.
        """

        # TODO: implement
        
        # The log turns the multiple to plus, 
        # and our approach is updating the whole tree from leaf to root
        
        symbol = int(symbol)
        
        
        self.log_kt+=self.log_kt_multiplier(symbol)
       
        #consistent with log_kt_multiplier function

        self.symbol_count[symbol]+=1
       
        #the probability is depend on the kt estimater, so
        # it should be update at end.
        self.update_log_probability()
        
    # end def

    def update_log_probability(self):
        """ This method calculates the logarithm of the weighted probability for this node.

            Assumes that `log_kt` and `log_probability` is correct for each child node.

              log(P^n_w) :=
                  log(Pr_kt(h_n)            (if n is a leaf node)
                  log(1/2 Pr_kt(h_n)) + 1/2 P^n0_w x P^n1_w)
                                            (otherwise)
            and stores the value in log_probability.
     
            Because of numerical issues, the implementation works directly with the
            log probabilities `log(Pr_kt(h_n)`, `log(P^n0_w)`,
            and `log(P^n1_w)` rather than the normal probabilities.

            To compute the second case of the weighted probability, we use the identity

                log(a + b) = log(a) + log(1 + exp(log(b) - log(a)))       a,b > 0

            to rearrange so that logarithms act directly on the probabilities:

                log(1/2 Pr_kt(h_n) + 1/2 P^n0_w P^n1_w) =

                    log(1/2) + log(Pr_kt(h_n))
                      + log(1 + exp(log(P^n0_w) + log(P^n1_w)
                                    - log(Pr_kt(h_n)))

                    log(1/2) + log(P^n0_w) + log(P^n1_w)
                      + log(1 + exp(log(Pr_kt(h_n)
                                           - log(P^n0_w) + log(P^n1_w)))

            In order to avoid overflow problems, we choose the formulation for which
            the argument of the exponent `exp(log(b) - log(a))` is as small as possible.
        """

        # TODO: implement
        #if it is leaf node, then the probability is just the kt-probability
        # otherwise, we calculate the probability based it's children.
        if self.is_leaf_node():
            
            self.log_probability = self.log_kt
            
        else:
            # as we update from leaf to root, thus the chirldren's probabiltiy
            # must already been updated.
            children = sum([subnode.log_probability for _,subnode in self.children.items()])
            # a > b -> smallest exp(log(b) - log(a))
            # a should be larger than b.
            a,b = sorted([self.log_kt,children],reverse = True)
            self.log_probability = log_half + a + math.log(1 + math.exp(b-a))
          
    # end def

    def visits(self):
        """ Returns the number of times this context has been visited.
            This is the sum of the visits of the (immediate) child nodes.
        """

        return self.symbol_count[0] + self.symbol_count[1]
    # end def
# end class
    
    
class CTWContextTree_Undo:
    
    '''
    Used to store the attributes of
    CTWContextTree, and we can revert symbols in 
    a efficient way.That trades the computation 
    power with storage.
    
    In order to revert a 24 bits sequence, assume we have 96 ctw depth.
    we need to do 24  * 96 constant operations in the traditional appraoch. However,
    Using the CTWContextTree_Undo class, we can revert CTWContextTree to previous state
    within 1 constant operations.

    '''
    
    def __init__(self, tree):
        
        for field,value in tree.__dict__.items():
            exec("self.field = deepcopy(value)")

class CTWContextTree:
    """ The high-level interface to an action-conditional context tree.
        Most of the mathematical details are implemented in the CTWContextTreeNode class, which is used to
        represent the nodes of the tree.
        CTWContextTree stores a reference to the root node of the tree (`root`), the history of
        updates to the tree (`history`), and the maximum depth of the tree (`depth`).

        It is primarily concerned with calling the appropriate functions in the appropriate nodes
        in order to deliver certain functionality:

        - `update(symbol_or_list_of_symbols)` updates the tree and the history
          after the agent has observed new percepts.

        - `update_history(symbol_or_list_of_symbols)` updates just the history
          after the agent has executed an action.

        - `revert()` reverts the last update to the tree.

        - `revert_history()` deletes the recent history.

        - `predict()` predicts the probability of future outcomes.

        - `generate_random_symbols_and_update()` samples a sequence from the
           context tree, updating the tree with each symbol as it is sampled.

        - `generate_random_symbols()` samples a sequence of a specified length,
           updating the tree with each symbol as it is sampled, then reverting all the
           updates so that the tree is in the same state as it was before the
           sampling.
    """

    def __init__(self, depth, estimate_size = None):
        """ Create a context tree of specified maximum depth.
            Nodes are created as needed.

            - `depth`: the maximum depth of the context tree.
        """

        # An list used to hold the nodes in the context tree that correspond to the current context.
        # It is important to ensure that `update_context()` is called before accessing the contents
        # of this list as they may otherwise be inaccurate.
        self.context = []

        # The maximum depth of the context tree.
        assert depth >= 0, "The given tree depth must be greater than zero."
        self.depth = depth

        # we only need depth-context at most, for safely reasons,
        # we consider the maximum bits need for mcts 
        # we can use this appraoch to save 
        # and speed up our algorithm
        
        if not estimate_size:
            estimate_size = 1000000000000
            
        self.size_of_history  = estimate_size + depth
        
        self.history = deque([],self.size_of_history)

        # The root node of the context tree.
        self.root = CTWContextTreeNode(tree = self)

        # The size of this tree.
        self.tree_size = 1
        
        #whether to trade the computation power with storage
        self.trade_off = False
    
    # end def
    
    def set_tade_off(self,value):
        '''
        set the trade off between computation power and storage
        only take bool value as  input. If the value is true,
        we will use the CTWContextTree_Undo class, otherwise 
        we use traditional approach in the revret operations.
        
        '''
        
        assert isinstance(value,bool),"invalid settings"
        
        self.trade_off = value
        
    def model_revert(self,undo_ctw):
        '''
        revert model to previous state
        
        '''
        
        for field,value in undo_ctw.__dict__.items():
            exec("self.field = value")

    def clear(self):
        """ Clears the entire context tree including all nodes and history.
        """

        # Reset the history.
        self.history = deque([],self.size_of_history)

        # Set a new root object, and reset the tree size.
        self.root.tree = None
        del self.root
        self.root = CTWContextTreeNode(tree = self)
        self.tree_size = 1

        # Reset the context.
        self.context = []
    # end def

    def generate_random_symbols(self, symbol_count):
        """ Returns a symbol string of a specified length by sampling from the context tree.

            - `symbol_count`: the number of symbols to generate.
        """
        symbol_list = self.generate_random_symbols_and_update(symbol_count)
        self.revert(symbol_count)

        return symbol_list
    # end def
    
    def maximum_likelihood_sequence(self,action_binary):
        
        '''
            action_binary: [[]]
            
            selection the maximum likelihood action
            - 'action_binary': [[]] : the list of binary representations of actons
        '''
        
        current_p = float("-INF")
        ml_action = None
        for action in action_binary:
            
            p = self.predict(action)
            
            if p > current_p:
                ml_action = action
                current_p = p
        
        return ml_action
        
        

    def generate_random_symbols_and_update(self, symbol_count):
        """ Returns a specified number of random symbols distributed according to
            the context tree statistics and update the context tree with the newly
            generated symbols.

            - `symbol_count`: the number of symbols to generate.
        """

        # TODO: implement
        
        sample =[]
        
        for index in range(symbol_count):
            
            # The theory is same as the Discrete Probability Mass Function
            # if we sample infinite bits at a particular history
            # Then the lim t->inf 1s/0s = self.predict(1) / self.predict(0),
            # as we choose the threshold from uniform distribution.
            # Consider the following sequence, b_1 b_2 …. b_d. 
            # The probability of having the sequence is  P = (b_1 b_2 …. b_d | history)  
            # and we could apply chain  rule P = (b_1 b_2 …. b_d | history)  =  
            # (b_2 …. b_d | history b_1) *  (b_1| history)
            #= (b_1| history) * (b_2| history b_2) * ….  (b_d | history b_1… b_(d-1) )
            
            sample.append(1 if self.predict(1) >= random.random() else 0)
            
            self.update(sample[-1])
        
        return sample
    # end def

    def predict(self, symbol_list):
        """ Returns the conditional probability of a symbol (or a list of symbols), considering the history.

            Given a history sequence `h` and a symbol `y`, the estimated probability is given by

              rho(y | h) = rho(hy)/rho(h)

            where `rho(h) = P_w^epsilon(h)` is the weighted probability estimate of observing `h`
            evaluated at the root node `epsilon` of the context tree.

            - `symbol_list` The symbol (or list of symbols) to estimate the conditional probability of.
                            0 corresponds to `rho(0 | h)` and 1 to `rho(1 | h)`.
        """

        # TODO: implement
        # consider the input is str, list or int.
        # if it is not list, we need to transfer to type int
        if isinstance(symbol_list,int):
            
            symbol_list = [symbol_list]
            
        else:
            
            symbol_list = list(symbol_list)
                               
        # As we are doing mixture Markov model, 
        # the largest order is depth-th order. 
        # The history length at least bigger than the depth.
        # If not, we can uniformly generate the history,
        # and doing the prediction.
        
        #note the root represent zero context
        difference  = self.depth  - len(self.history)
        
        if difference > 0:
            #by doing this, please keep in mind, please reset the whole (exclude the real history)
            #tree after each mc-simulation if the history < tree depth before mc-simulation.
            self.update([random.randint(0,1) for i in range(difference)])
        
        h  = self.root.log_probability
        
        #trading the storage with computation power
        if self.trade_off:
            
            undo_ctw = CTWContextTree_Undo(self)
            
        self.update(symbol_list)
        
        hy = self.root.log_probability
        
        if self.trade_off:
            
            self.model_revert(undo_ctw)
            
        else:
            
            self.revert(len(symbol_list))
        
        # log a - log b = log (a/b)
        # exp**(log a - log b) = a/b
        # transfer the log back
        p = math.exp(hy - h)
        
        return p
    # end def

    def revert(self, symbol_count = 1):
        """ Restores the context tree to its state prior to a specified number of updates.
     
            - `num_symbols`: the number of updates (symbols) to revert. (Default of 1.)
        """
        # TODO: implement
        
        assert len(self.history) >= symbol_count, "Cannot revert, symbol_count bigger than the length of history"
        
        difference = len(self.history) - symbol_count
        
        # if the reverted history will have  len(history) < self.depth
        # then we just delete whole tree, and store part of hitstory. The situation could 
        # happends on the begining, as if the ctw depth is large. The initial perception cannot
        # provide enough context for the incoming bits.
        # If we revert it, we will result in a invalid log probability which bigger than 0
        # then the convergency speed will be influenced. 
        if difference < self.depth :
            history = deepcopy(list(self.history)[:difference+1])
            self.clear()
            self.history += history
            
            return None
        
        # revert the tree in reversed order
        # because of the dependency relationships.
        
        for step in range(symbol_count):
            
            bit = self.history.pop()
            
            self.update_context()
            
            for node in reversed(self.context):
                
                node.revert(bit)
                
    # end def

    def revert_history(self, symbol_count = 1):
        """ Shrinks the history without affecting the context tree.
        """

        assert symbol_count > 0, "The given symbol count should be greater than 0."
        history_length = len(self.history)
        assert history_length >= symbol_count, "The given symbol count must be greater than the history length."

        new_size = history_length - symbol_count
        self.history = deque(list(self.history)[:new_size],self.size_of_history)
    # end def

    def size(self):
        """ Returns the number of nodes in the context tree.
        """

        # Return the value stored and updated by the children nodes.
        return self.tree_size
    # end def

    def update(self, symbol_list):
        """ Updates the context tree with a new (binary) symbol, or a list of symbols.
            Recalculates the log weighted probabilities and log KT estimates for each affected node.

            - `symbol_list`: the symbol (or list of symbols) with which to update the tree.
                              (The context tree is updated with symbols in the order they appear in the list.)
        """

        # TODO: implement
        # consider the input is str, list or int.
        # if it is not list, we need to transfer to type int
        if isinstance(symbol_list,int):
            
            symbol_list = [symbol_list]
            
        else:
            
            symbol_list = list(symbol_list)
        
        for bit in symbol_list:
            
            bit = int(bit)
            
            #cannot update context if the history is too short
            #As the depth is represents k-th order Markov model
            #Thus, at least len(k) history in the context
            
            if len(self.history) < self.depth :
                
                self.update_history(bit)
                
                continue
            
            self.update_context()
            
            # update the tree in reversed order,
            # because of the dependency relationship.
            
            for node in reversed(self.context):
                
                node.update(bit)
                
            self.update_history(bit)
        
            
    # end def

    def update_context(self):
        """ Calculates which nodes in the context tree correspond to the current
            context, and adds them to `context` in order from root to leaf.

            In particular, `context[0]` will always correspond to the root node
            and `context[self.depth]` corresponds to the relevant leaf node.

            Creates the nodes if they do not exist.
        """

        # TODO: implement
        
        '''
        R for root, C for Children , b for new bit
        eg: depth 3, history 110001b
                                CCCR 
                                
        empty string, 1, 01, 001 is the context of b.
        and context is found from tree leaf to node.
        please read the context from right to left.
        
        '''
        
        context = [self.root]
        last_node = self.root
        
        for bit in reversed(list(self.history)[-self.depth:]):
            
            # if value is 1, go left branch, otherwise right branch
            index = 1 if bit else 0
            
            if index not in context[-1].children:
                
                last_node.children[index] = CTWContextTreeNode(self)
                
                #update last node in the context list, as we create new child.
                context[-1] = last_node
                
            context.append(context[-1].children[index])
                
            last_node = context[-1]
                    
        self.context = context
        
        
    # end def

    def update_history(self, symbol_list):
        """ Appends a symbol (or a list of symbols) to the tree's history without updating the tree.

            - `symbol_list`: the symbol (or list of symbols) to add to the history.
        """

        # Ensure that we have a list, by making this a list if it's a single symbol.
        if type(symbol_list) != list:
            symbol_list = [symbol_list]
        # end if

        self.history += symbol_list
    # end def
# end class