import gym
import jsbsim_gym # This line makes sure the environment is registered
from os import path
from stable_baselines3 import SAC


env = gym.make("JSBSim-v1",render_mode='flightgear')

model = SAC.load("models/jsbsim_sac", env)

obs = env.reset()
done = False
step = 0
while not done:
    env.render()
    action, _ = model.predict(obs, deterministic=True)
    obs, _, done, _ = env.step(action)
    step += 1
env.close()
print(step)