import time

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.crazyflie.syncLogger import SyncLogger

URI = 'radio://0/30/2M/E7E7E7E7E7'

cflib.crtp.init_drivers(enable_debug_driver=False)

with SyncCrazyflie(URI, cf=Crazyflie(rw_cache='./cache')) as scf:
    mc = MotionCommander(scf)
    mc.take_off(1.0, 0.3)

    try:
        while True:
            time.sleep(1)
            mc.forward(0.5)
            mc.right(0.5)
            mc.back(0.5)
            mc.left(0.5)
    except KeyboardInterrupt:
        ctol.land()
