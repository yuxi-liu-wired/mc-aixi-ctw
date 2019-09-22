
from pyaixi import agent, prediction, search, util, environment, environments
from mc_aixi_ctw import MC_AIXI_CTW_Agent
from pyaixi.environment import Environment
from pyaixi.environments.coin_flip import CoinFlip

import pytest

m = 10 # agent horizon
d = 10 # CT depth
s = 10 # number of simulations
env = CoinFlip()

options = {'agent-horizon': m,
           'ct-depth': d,
           'mc-simulations': s}

aixi = MC_AIXI_CTW_Agent(env, options)
aixi.generate_percept()

