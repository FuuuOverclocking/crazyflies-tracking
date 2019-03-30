import time

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.crazyflie.syncLogger import SyncLogger
from cflib.positioning.motion_commander import MotionCommander

URI = 'radio://0/30/2M/E7E7E7E7E7'

cflib.crtp.init_drivers(enable_debug_driver=False)

with SyncCrazyflie(URI, cf=Crazyflie(rw_cache='./cache')) as scf:
    mc = MotionCommander(scf)
    mc.take_off(1.0, 0.3)
    # 利用更底层函数精确指定悬浮高度为 1m
    scf.cf.commander.send_hover_setpoint(0, 0, 0, 1.0)
    mc._thread._z_base = 1.0
    mc._thread._z_velocity = 0.0
    mc._thread._z_base_time = time.time()
    time.sleep(1)

    try:
        while True:
            time.sleep(1)
            mc.forward(0.5, 0.3)
            mc.right(0.5, 0.3)
            mc.back(0.5, 0.3)
            mc.left(0.5, 0.3)
    except:
        mc.land()
