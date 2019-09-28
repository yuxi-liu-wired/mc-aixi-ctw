
#from pyaixi import agent, prediction, search, util, environment, environments
from mc_aixi_ctw import MC_AIXI_CTW_Agent
from pyaixi.environment import Environment
from pyaixi.environments.coin_flip import CoinFlip
from pyaixi.environments.pac_man import PacMan
from pyaixi.agent import update_enum, action_update, percept_update

import pytest

m = 4 # agent horizon
d = 10 # CT depth
s = 10 # number of simulations
env = CoinFlip()

options = {'agent-horizon': m,
           'ct-depth': d,
           'mc-simulations': s}

print("---======== BEGIN TEST ========---")
print("\tCoinFlip environment")
aixi = MC_AIXI_CTW_Agent(env, options)


#### initial percept should always be (0,0) and last update must be percept_update
print("++++ Generate initial percept:")
percept = aixi.generate_percept_and_update()
def initial_percept():
    assert percept == (0,0), "initial percept is not (0,0)"
    assert aixi.last_update == percept_update, "last update is not percept_update"
    print("* environment succesfully recorded initial percept "+str(percept))
initial_percept()


#### check if action is in action space
print("++++ Search for optimal action:")
action = aixi.search()
def action_is_in_action_space():
    assert action in aixi.environment.valid_actions, "action is not in action space"
    print("* agent succesfully performed valid action "+str(action))
action_is_in_action_space()


#### check if action is recorded in environment
print("++++ Record selected actionin environment:")
aixi.model_update_action(action)
def action_is_recorded_in_env():
    assert action == aixi.environment.action, "environment did not record last action"
    assert aixi.last_update == action_update, "last update is not action_update"
    print("* environment succesfully recorded action "+str(action))
action_is_recorded_in_env()

print("* environment status:\n\t"+aixi.environment.print())
print("---======== END TEST ========---")

print("\n\n\n")


m = 4 # agent horizon
d = 10 # CT depth
s = 10 # number of simulations
env = PacMan()

options = {'agent-horizon': m,
           'ct-depth': d,
           'mc-simulations': s}

print("---======== BEGIN TEST ========---")
print("\tPacMan environment")
aixi = MC_AIXI_CTW_Agent(env, options)


#### initial percept should always be (0,0) and last update must be percept_update
print("++++ Generate initial percept:")
percept = aixi.generate_percept_and_update()
print(percept)
def initial_percept():
    assert percept[0] <=2**16 and percept[0] >=0, "initial percept is not (0,0)"
    assert aixi.last_update == percept_update, "last update is not percept_update"
    print("* environment succesfully recorded initial percept "+str(percept))
initial_percept()


#### check if action is in action space
print("++++ Search for optimal action:")
action = aixi.search()
def action_is_in_action_space():
    assert action in aixi.environment.valid_actions, "action is not in action space"
    print("* agent succesfully performed valid action "+str(action))
action_is_in_action_space()


#### check if action is recorded in environment
print("++++ Record selected actionin environment:")
aixi.model_update_action(action)
def action_is_recorded_in_env():
    assert action == aixi.environment.action, "environment did not record last action"
    assert aixi.last_update == action_update, "last update is not action_update"
    print("* environment succesfully recorded action "+str(action))
action_is_recorded_in_env()

print("* environment status:\n\t"+aixi.environment.print())


