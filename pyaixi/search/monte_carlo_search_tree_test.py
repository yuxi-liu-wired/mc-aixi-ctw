from pyaixi.search.monte_carlo_search_tree import mcts_planning, MonteCarloSearchNode
from pyaixi.agents.mc_aixi_ctw import MC_AIXI_CTW_Agent
from pyaixi.environments.coin_flip import CoinFlip
from pyaixi.agent import update_enum, action_update, percept_update

import pytest

m = 5 # agent horizon
d = 5 # CT depth
s = 5 # number of simulations
env = CoinFlip()

options = {'agent-horizon': m,
           'ct-depth': d,
           'mc-simulations': s}

print("---======== BEGIN TEST ========---")

aixi = MC_AIXI_CTW_Agent(env, options)
percept = aixi.generate_percept_and_update()

sampled_action = mcts_planning(aixi, aixi.horizon, aixi.mc_simulations)

print("Sampled action: "+str(sampled_action))

