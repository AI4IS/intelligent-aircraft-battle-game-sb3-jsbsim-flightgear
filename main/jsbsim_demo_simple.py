import jsbsim
import os
import numpy as np
import time

# TODO: 收起落架

SIM_PATH = 'C:\\BVR\\CloseAirCombat\\envs\\JSBSim\\data'
MODEL = 'f16'
COLOR = 'Red'
DT = 1/720
DOWN_SAMPLE_STEP = 12
TOTAL_STEP = 1000
UID = 'A0100'
IS_RECORD = False
STATE_LIST = [
    'position/long-gc-deg',
    'position/lat-geod-deg',
    'position/h-sl-ft',
    'velocities/mach',
    'aero/alpha-rad',
    'aero/beta-rad',
    'velocities/p-rad_sec',
    'velocities/q-rad_sec',
    'velocities/r-rad_sec',
    'attitude/phi-rad',    # 与12相同
    'attitude/theta-rad',  # 与13相同
    'attitude/psi-rad',    # 与14相同
    'attitude/roll-rad',
    'attitude/pitch-rad',
    'attitude/heading-true-rad',
]

def get_sim_time():
    """ Gets the simulation time from JSBSim, a float. """
    return jsbsim_exec.get_sim_time()

def step():
    for _ in range(DOWN_SAMPLE_STEP): # 12 / 60 per step time
        jsbsim_exec.set_property_value('fcs/aileron-cmd-norm',0.3)
        jsbsim_exec.set_property_value('fcs/elevator-cmd-norm',-0.5)
        jsbsim_exec.set_property_value('fcs/throttle-cmd-norm',1)
        jsbsim_exec.set_property_value('fcs/rudder-cmd-norm',0.2)
        result = jsbsim_exec.run()
        if not result:
            raise RuntimeError("JSBSim failed.")
        if jsbsim_exec.get_property_value(STATE_LIST[2]) <= 0:
            raise RuntimeError("Low height!")

def print_state():
    for i in range(15):
        print(STATE_LIST[i], state[i], end='\t')
    print()

def render(mode="flightgear", filepath='./JSBSimRecording.txt.acmi'):
        if mode == "txt":
            global IS_RECORD
            if not IS_RECORD: # create once
                with open(filepath, mode='w', encoding='utf-8-sig') as f:
                    f.write("FileType=text/acmi/tacview\n")
                    f.write("FileVersion=2.1\n")
                    f.write("0,ReferenceTime=2020-04-01T8:00:00Z\n")
                IS_RECORD = True
            with open(filepath, mode='a', encoding='utf-8-sig') as f:
                timestamp = step_cnt * DOWN_SAMPLE_STEP * DT
                f.write(f"#{timestamp:.2f}\n")
                # single sim
                lon = jsbsim_exec.get_property_value(STATE_LIST[0])
                lat = jsbsim_exec.get_property_value(STATE_LIST[1])
                alt = jsbsim_exec.get_property_value(STATE_LIST[2]) * 0.3048
                roll = jsbsim_exec.get_property_value(STATE_LIST[12]) * 180 / np.pi
                pitch = jsbsim_exec.get_property_value(STATE_LIST[13]) * 180 / np.pi
                yaw = jsbsim_exec.get_property_value(STATE_LIST[14]) * 180 / np.pi
                log_msg = f"{UID},T={lon}|{lat}|{alt}|{roll}|{pitch}|{yaw},"
                log_msg += f"Name={MODEL.upper()},"
                log_msg += f"Color={COLOR}"
                if log_msg is not None:
                    f.write(log_msg + "\n")

        # TODO: real time rendering [Use FlightGear, etc.]
        elif mode == 'flightgear':
            # jsbsim_exec.set_output_directive('data_output/flightgear{}.xml'.format(1))
            time.sleep(0.05)
        else:
            raise NotImplementedError

state = np.zeros(15)

# load JSBSim FDM
jsbsim_exec = jsbsim.FGFDMExec(SIM_PATH)
jsbsim_exec.set_debug_level(0)
# flightgear visualization (Must be in front of load_model method)
jsbsim_exec.set_output_directive('data_output/flightgear{}.xml'.format(1))

jsbsim_exec.load_model(MODEL)
jsbsim_exec.query_property_catalog("")
jsbsim_exec.set_dt(DT)

# load JSBSim FDM
jsbsim_exec.set_property_value('ic/long-gc-deg',120.0)
jsbsim_exec.set_property_value('ic/lat-geod-deg',60.0)
jsbsim_exec.set_property_value('ic/h-sl-ft',20000)
jsbsim_exec.set_property_value('ic/psi-true-deg',0.0)
jsbsim_exec.set_property_value('ic/u-fps',800.0)
jsbsim_exec.set_property_value('ic/v-fps',0.0)
jsbsim_exec.set_property_value('ic/w-fps',0.0)
jsbsim_exec.set_property_value('ic/p-rad_sec',0.0)
jsbsim_exec.set_property_value('ic/q-rad_sec',0.0)
jsbsim_exec.set_property_value('ic/r-rad_sec',0.0)
jsbsim_exec.set_property_value('ic/roc-fpm',0.0)
jsbsim_exec.set_property_value('ic/terrain-elevation-ft',0)


# ... other propterty

success = jsbsim_exec.run_ic()

if not success:
    raise RuntimeError("JSBSim failed to init simulation conditions.")

# propulsion init running
propulsion = jsbsim_exec.get_propulsion()
n = propulsion.get_num_engines()
for j in range(n):
    propulsion.get_engine(j).init_running()
propulsion.get_steady_state()



step_cnt = 0

# run
while True:
    step()
    step_cnt += 1
    for i, property in enumerate(STATE_LIST):
        state[i] = jsbsim_exec.get_property_value(property)

    print(get_sim_time())
    print_state()
    # render()
    if step_cnt == TOTAL_STEP:
        break

