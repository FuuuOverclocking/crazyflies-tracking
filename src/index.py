import time

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.crazyflie.syncLogger import SyncLogger

from data import Data
from controller import Controller

URI = 'radio://0/30/2M/E7E7E7E7E7'

cflib.crtp.init_drivers(enable_debug_driver=False)

log_config = LogConfig(name='Position', period_in_ms=40)
# log_config.add_variable('kalman.stateX', 'float')
# log_config.add_variable('kalman.stateY', 'float')
log_config.add_variable('ranging.distance0', 'float')
# log_config.add_variable('kalman.stateZ', 'float')
# log_config.add_variable('stabilizer.roll', 'float')

data = Data()

def log_handler(timestamp, _data, logconf):
    data.update(timestamp, _data, logconf)

with SyncCrazyflie(URI, cf=Crazyflie(rw_cache='./cache')) as scf:
    scf.cf.log.add_config(log_config)
    log_config.data_received_cb.add_callback(log_handler)
    log_config.start()

    mc = MotionCommander(scf)

    ctol = Controller(data, mc)

    mc.take_off(1.0, 0.3)

    try:
        while True:
            ctol.tick()
    except KeyboardInterrupt:
        ctol.land()
