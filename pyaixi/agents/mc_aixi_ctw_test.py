
#from pyaixi import agent, prediction, search, util, environment, environments
from mc_aixi_ctw import MC_AIXI_CTW_Agent
from pyaixi.environment import Environment
from pyaixi.environments.coin_flip import CoinFlip
from pyaixi.agent import update_enum, action_update, percept_update

import pytest

m = 10 # agent horizon
d = 10 # CT depth
s = 10 # number of simulations
env = CoinFlip()

options = {'agent-horizon': m,
           'ct-depth': d,
           'mc-simulations': s}

aixi = MC_AIXI_CTW_Agent(env, options)
percept = aixi.generate_percept_and_update()

#initial percept always (0,0) and last update must be percept_update
def initial_percept():
    assert percept == (0,0), "initial percept is not (0,0)"
    assert aixi.last_update == percept_update, "last update is not percept_update"
initial_percept()

action = aixi.search()

#action = aixi.generate_action()

