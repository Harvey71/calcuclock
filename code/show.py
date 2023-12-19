from display import Display
from clock import Clock
from setup import Setup
from bat import Battery
from machine import deepsleep

def show():
    setup = Setup()
    df_name, tz_name = setup.read_config()
    display = Display()
    clock = Clock(df_name, tz_name)
    battery = Battery()
    
    cap, loading, drained = battery.status()
    
    if drained:
        display.draw_battery(400, 240, cap, loading, drained, bs=8)
        display.show()
        display.sleep()
        deepsleep(60000)
    else:
        hs, ms, ds = clock.get_strings(offset=5)
        display.big_text(hs, 52, 25)
        display.big_text(ms, 52, 225)
        display.text(ds, 52, 425)
        display.draw_battery(690, 440, cap, loading, drained, bs=3)
        display.show()
        display.sleep()
        y, mm, d, h, m, s, w, dd = clock.read()
        delay = max(55 - s, 1)
        deepsleep(delay * 1000)
