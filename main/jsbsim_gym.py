import jsbsim
import gym
import numpy as np
import time
import math

# Initialize format for the environment state vector
STATE_FORMAT = [
    'position/long-gc-deg',
    'position/lat-geod-deg',
    'position/h-sl-ft',
    "velocities/mach",
    "aero/alpha-rad",
    "aero/beta-rad",
    "velocities/p-rad_sec",
    "velocities/q-rad_sec",
    "velocities/r-rad_sec",
    'attitude/roll-rad',
    'attitude/pitch-rad',
    'attitude/heading-true-rad',
]

STATE_LOW = np.array([
    -np.inf,
    -np.inf,
    0,
    0,
    -np.pi,
    -np.pi,
    -np.inf,
    -np.inf,
    -np.inf,
    -np.pi,
    -np.pi,
    -np.pi,
    -np.inf,
    -np.inf,
    0,
])

STATE_HIGH = np.array([
    np.inf,
    np.inf,
    np.inf,
    np.inf,
    np.pi,
    np.pi,
    np.inf,
    np.inf,
    np.inf,
    np.pi,
    np.pi,
    np.pi,
    np.inf,
    np.inf,
    np.inf,
])

# You need to git clone jsbsim official project to your local environment and fill the path into SIM_PATH
SIM_PATH = 'JSBSIM OFFICIAL PROJECT PATH'
class JSBSimEnv(gym.Env):
    def __init__(self, root=SIM_PATH, render_mode='txt'):
        super().__init__()
        self.dt = 1/60
        self.down_sample_step = 3
        self.state = np.zeros(12)
        self.goal = np.zeros(3)
        self.step_cnt = 0
        # only for tacview render
        self.uid = 'A0100'
        self.is_tacview_record = False
        self.color = 'Red'
        self.model = 'f16'
        self.render_mode = render_mode

        # Set observation and action space format
        self.observation_space = gym.spaces.Box(STATE_LOW, STATE_HIGH, (15,))
        self.action_space = gym.spaces.Box(np.array([-1,-1,-1,0]), 1, (4,))

        # Initialize JSBSim
        self.sim = jsbsim.FGFDMExec(root, None)
        self.sim.set_debug_level(0)
        # flightgear render init
        self.sim.set_output_directive('data_output/flightgear{}.xml'.format(1))
        if self.render_mode == 'flightgear':
            self.sim.set_output_directive('data_output/flightgear{}.xml'.format(1))
        
        self.sim.load_model(self.model)
        self.sim.query_property_catalog("")
        self.sim.set_dt(self.dt)
        self._set_initial_conditions()
        success = self.sim.run_ic()
        if not success:
            raise RuntimeError("JSBSim failed to init simulation conditions.")
        
    def _set_initial_conditions(self):
         # load JSBSim FDM
        self.sim.set_property_value('ic/long-gc-deg',120.0)
        self.sim.set_property_value('ic/lat-geod-deg',60.0)
        self.sim.set_property_value('ic/h-sl-ft',20000)
        self.sim.set_property_value('ic/psi-true-deg',0.0)
        self.sim.set_property_value('ic/u-fps',800.0)
        self.sim.set_property_value('ic/v-fps',0.0)
        self.sim.set_property_value('ic/w-fps',0.0)
        self.sim.set_property_value('ic/p-rad_sec',0.0)
        self.sim.set_property_value('ic/q-rad_sec',0.0)
        self.sim.set_property_value('ic/r-rad_sec',0.0)
        self.sim.set_property_value('ic/roc-fpm',0.0)
        self.sim.set_property_value('ic/terrain-elevation-ft',0)
        # ... other propterty

        # propulsion init running
        propulsion = self.sim.get_propulsion()
        n = propulsion.get_num_engines()
        for j in range(n):
            propulsion.get_engine(j).init_running()
        propulsion.get_steady_state()
        self.sim.set_property_value('propulsion/set-running', -1)

    def get_sim_time(self):
        """ Gets the simulation time from JSBSim, a float. """
        return self.sim.get_sim_time()

    def step(self, action):
        roll_cmd, pitch_cmd, yaw_cmd, throttle = action

        # Pass control inputs to JSBSim
        self.sim.set_property_value('fcs/aileron-cmd-norm', roll_cmd)
        self.sim.set_property_value('fcs/elevator-cmd-norm', pitch_cmd)
        self.sim.set_property_value('fcs/throttle-cmd-norm', throttle)
        self.sim.set_property_value('fcs/rudder-cmd-norm', yaw_cmd)

        # every env step execute down_sample_step sim steps
        for _ in range(self.down_sample_step):
            # Freeze fuel consumption
            self.sim.set_property_value("propulsion/tank/contents-lbs", 1000)
            self.sim.set_property_value("propulsion/tank[1]/contents-lbs", 1000)

            # Set gear up
            self.sim.set_property_value("gear/gear-cmd-norm", 0.0)
            self.sim.set_property_value("gear/gear-pos-norm", 0.0)

            result = self.sim.run()
            if not result:
                raise RuntimeError("JSBSim run failed.")
            
        # Get the JSBSim state and save to self.state
        self._get_state()

        # reward
        reward = 0

        # done
        done = False

        # collision with ground
        if self.state[2] * 0.3048 < 100:
            reward = -10
            done = True
               

        self.step_cnt += 1

        return np.hstack([self.state, self.goal]), reward, done, {}
    
    def _get_state(self):
        # Gather all state properties from JSBSim
        for i, property in enumerate(STATE_FORMAT):
            self.state[i] = self.sim.get_property_value(property)

    def reset(self, seed=None):
        self._set_initial_conditions()
        self.sim.run_ic()

        # Generate a new goal
        
        # Get state and save
        self._get_state()

        self.step_cnt = 0
        return np.hstack([self.state,self.goal])
    
    def render(self, mode='txt'):
        if self.render_mode == 'txt':
            filepath = './JSBSimRecording.txt.acmi'
            if not self.is_tacview_record: # create once
                with open(filepath, mode='w', encoding='utf-8-sig') as f:
                    f.write("FileType=text/acmi/tacview\n")
                    f.write("FileVersion=2.1\n")
                    f.write("0,ReferenceTime=2020-04-01T8:00:00Z\n")
                self.is_tacview_record = True
            with open(filepath, mode='a', encoding='utf-8-sig') as f:
                timestamp = self.step_cnt * self.down_sample_step * self.dt
                f.write(f"#{timestamp:.2f}\n")
                # single sim
                lon = self.sim.get_property_value(STATE_FORMAT[0])
                lat = self.sim.get_property_value(STATE_FORMAT[1])
                alt = self.sim.get_property_value(STATE_FORMAT[2])*0.3048
                roll = self.sim.get_property_value(STATE_FORMAT[9]) * 180 / np.pi
                pitch = self.sim.get_property_value(STATE_FORMAT[10]) * 180 / np.pi
                yaw = self.sim.get_property_value(STATE_FORMAT[11]) * 180 / np.pi
                log_msg = f"{self.uid},T={lon}|{lat}|{alt}|{roll}|{pitch}|{yaw},"
                log_msg += f"Name={self.model.upper()},"
                log_msg += f"Color={self.color}"
                if log_msg is not None:
                    f.write(log_msg + "\n")

        elif self.render_mode == 'flightgear':
            self.sim.set_output_directive('data_output/flightgear{}.xml'.format(1))
            time.sleep(self.down_sample_step * self.dt)
        else:
            # raise NotImplementedError
            pass

    def close(self):
        pass

class WrapperReward(gym.Wrapper):
    def __init__(self, env, gain):
        super().__init__(env)
        self.gain = gain
    
    # You can design your own reward function here.
    def step(self, action):
        obs, reward, done, info = super().step(action)
        # level safe flight
        heading_error_scale = 5.0  # degrees
        if obs[9] > np.pi:
            obs[9] = obs[9] - 2*np.pi
        if obs[11] > np.pi:
            obs[11] = obs[11] - 2*np.pi
        heading_r = math.exp(-((obs[11] / heading_error_scale) ** 2))
        # alt_error_scale = 15.24  # m
        # alt_r = math.exp(-(((obs[2]*0.3048 - 3000*0.3048) / alt_error_scale) ** 2))

        roll_error_scale = 0.35  # radians ~= 20 degrees
        roll_r = math.exp(-((obs[9] / roll_error_scale) ** 2))

        # speed_error_scale = 24  # mps (~10%)
        # speed_r = math.exp(-(((obs[3]*340 - 280) / speed_error_scale) ** 2))

        reward += (heading_r * roll_r) ** (1 / 2)
        return obs, reward, done, info
    
    def reset(self):
        obs = super().reset()
        return obs
    
    
def wrap_jsbsim(**kwargs):
    return WrapperReward(JSBSimEnv(**kwargs), 1)

# Register the wrapped environment
gym.register(
    id="JSBSim-v1",
    entry_point=wrap_jsbsim,
    max_episode_steps=1200
)

# Short example script to create and run the environment with
# constant action for 1 simulation second.
if __name__ == "__main__":
    env = JSBSimEnv(render_mode='txt')
    env.reset()
    for _ in range(1200):
        env.step(np.array([0.05, -0.2, 0, 0.5]))
        env.render()
    env.close()
