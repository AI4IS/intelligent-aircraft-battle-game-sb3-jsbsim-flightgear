import gym
import jsbsim_gym
from os import path
from stable_baselines3 import SAC

env = gym.make("JSBSim-v1", render_mode='flightgear')

log_path = path.join(path.abspath(path.dirname(__file__)), 'logs')

try:
    model = SAC('MlpPolicy', env, verbose=1, tensorboard_log=log_path, gradient_steps=-1, device='cpu')
    model.learn(3000000)
finally:
    model.save("models/jsbsim_sac")
    model.save_replay_buffer("models/jsbsim_sac_buffer")

# TODO 1: add wandb record
# TODO 2: multi agent flightgear render (> 2)