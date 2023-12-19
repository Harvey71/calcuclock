import machine
cause = machine.reset_cause()
print('Hello world', cause)

factory_reset = False
pwr_read_test = False

if pwr_read_test:
    from bat import Battery
    b = Battery()
    b.test()
elif factory_reset:
    from display import clear
    clear()
elif cause in (1,3):
    from setup import setup_show
    import machine
    setup_show()
    machine.reset()
elif cause == 2:
    from setup import setup_server
    import machine
    setup_server()
else:
    from show import show
    show()
    