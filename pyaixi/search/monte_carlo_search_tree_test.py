from pyaixi.search.monte_carlo_search_tree import mcts_planning, MonteCarloSearchNode, decision_node, chance_node
from pyaixi.agents.mc_aixi_ctw import MC_AIXI_CTW_Agent
from pyaixi.environments.coin_flip import CoinFlip
from pyaixi.environments.cheese_maze import CheeseMaze
from pyaixi.environments.extended_tiger import ExtendedTiger
from pyaixi.environments.kuhn_poker import KuhnPoker
from pyaixi.environments.pac_man import PacMan
from pyaixi.agent import update_enum, action_update, percept_update

import pytest
import random


def mc_iter(aixi):
    print("\n\n=========== Sample ===========")
    samp = mc_tree.sample(aixi, m)
    print(" * Exp.reward of root: "+str(mc_tree.mean))
    print(" * got reward sample: "+str(samp))
    
    print("\t** hist size: "+str(aixi.history_size()))
    print("\t** agent age: "+str(aixi.age))
    print("\t** agent tot reward: "+str(aixi.total_reward))
    print("CTW history: "+str(aixi.context_tree.history))
    print("env status:\n\t"+aixi.environment.print())


m = 5 # agent horizon
d = 10 # CT depth
s = 10 # number of simulations
env = CoinFlip()

options = {'agent-horizon': m,
           'ct-depth': d,
           'mc-simulations': s}

print("---======== BEGIN TEST ========---")
"""
tried seed:
    15 - correct preds up to 4 samples
"""
random.seed(5)

aixi = MC_AIXI_CTW_Agent(env, options)
percept = aixi.generate_percept_and_update()
print("get initial percept: "+str(percept))

mc_tree = MonteCarloSearchNode(decision_node)

print("\n\n=========== Sample ===========")
samp = mc_tree.sample(aixi, m)
print(" * Exp.reward of root: "+str(mc_tree.mean))
print(" * Root children: "+str(mc_tree.children))
print(" * got reward sample: "+str(samp))

print("\t** hist size: "+str(aixi.history_size()))
print("\t** agent age: "+str(aixi.age))
print("\t** agent tot reward: "+str(aixi.total_reward))
print("CTW history: "+str(aixi.context_tree.history))
print("env status:\n\t"+aixi.environment.print())


mc_iter(aixi)

mc_iter(aixi)

mc_iter(aixi)

mc_iter(aixi)

mc_iter(aixi)

mc_iter(aixi)

mc_iter(aixi)

#sampled_action = mcts_planning(aixi, aixi.horizon, aixi.mc_simulations)
#print("Sampled action: "+str(sampled_action))

