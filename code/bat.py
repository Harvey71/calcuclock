import machine
import display
import time

class Battery:
    
    def __init__(self):
        self.a0 = machine.ADC(machine.Pin(36), atten=machine.ADC.ATTN_11DB)
        self.a1 = machine.ADC(machine.Pin(39), atten=machine.ADC.ATTN_11DB)

    def status(self):
        samples = 3
        rawbat = 0
        rawpwr = 0
        for i in range(samples):
            rawbat += self.a0.read()
            rawpwr += self.a1.read()
        rawbat /= samples
        rawpwr /= samples
        vbat = (rawbat + 270) / 630
        vpwr = (rawpwr + 270) / 630
        loading = (vpwr - vbat) > 0.2
        cap = 0
        drained = False
        if not loading:
            cap = 100
            cap = round((vbat - 2.6) / 1.2 * 100)
            cap = max(0, cap)
            cap = min(100, cap)
            if cap == 0:
                drained = True
        return cap, loading, drained
            
    def test(self):
        import display
        d = display.Display()

        while True:
            rawbat = self.a0.read()
            rawpwr = self.a1.read()
            d.text(f'rawbat: {rawbat}', 10, 60)
            d.text(f'rawpwr: {rawpwr}', 10, 110)
            d.show()
            time.sleep_ms(1000)   
