from pyaixi.search.monte_carlo_search_tree import mcts_planning, MonteCarloSearchNode, decision_node, chance_node
from pyaixi.agents.mc_aixi_ctw import MC_AIXI_CTW_Agent
from pyaixi.environments.coin_flip import CoinFlip
from pyaixi.agent import update_enum, action_update, percept_update

import pytest
import random

m = 5 # agent horizon
d = 10 # CT depth
s = 10 # number of simulations
env = CoinFlip()

options = {'agent-horizon': m,
           'ct-depth': d,
           'mc-simulations': s}

print("---======== BEGIN TEST ========---")
random.seed(15)

aixi = MC_AIXI_CTW_Agent(env, options)
percept = aixi.generate_percept_and_update()


rollout_r = aixi.playout(6)
print("test rollout, got: "+str(rollout_r))

mc_tree = MonteCarloSearchNode(decision_node)

print("\n======= Sample =======")
samp = mc_tree.sample(aixi, m)
print(" * Exp.reward of root: "+str(mc_tree.mean))
print(" * Root children: "+str(mc_tree.children))
print(" * got sample: "+str(samp))

print("\n======= Sample =======")
samp = mc_tree.sample(aixi, m)
print(" * Exp.reward of root: "+str(mc_tree.mean))
print(" * Root children: "+str(mc_tree.children))
print(" * got sample: "+str(samp))

print("\n======= Sample =======")
samp = mc_tree.sample(aixi, m)
print(" * Exp.reward of root: "+str(mc_tree.mean))
print(" * Root children: "+str(mc_tree.children))
print(" * got sample: "+str(samp))

print("\n======= Sample =======")
samp = mc_tree.sample(aixi, m)
print(" * Exp.reward of root: "+str(mc_tree.mean))
print(" * Root children: "+str(mc_tree.children))
print(" * got sample: "+str(samp))

print("\n======= Sample =======")
samp = mc_tree.sample(aixi, m)
print(" * Exp.reward of root: "+str(mc_tree.mean))
print(" * Root children: "+str(mc_tree.children))
print(" * got sample: "+str(samp))


#print("\n======= Sample =======")
#samp = mc_tree.children[0].sample(aixi, m)

#print(aixi.environment.print())

#sampled_action = mcts_planning(aixi, aixi.horizon, aixi.mc_simulations)
#print("Sampled action: "+str(sampled_action))

