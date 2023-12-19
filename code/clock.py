import machine
import time
import random
import os

dt_formats = {
    'English': {
        'weekdays' :['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
        'format': '%w, %mm/%d/%y',
    },
    'German': {
        'weekdays' :['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag'],
        'format': '%w, %d.%mm.%y',
    },
}

class Clock:
    
    def __init__(self, df_name = None, tz_name = None):
        self.i2c = machine.SoftI2C(sda=machine.Pin(21), scl=machine.Pin(22))
        self.tz_data = None
        self.dt_format = None
        self.weekdays = None
        if tz_name:
            try:
                tz_module = __import__('_zones/' + tz_name)
                self.tz_data = tz_module.tz_data
            except:
                self.tz_data = None
        if df_name:
            self.dt_format = dt_formats.get(df_name, {}).get('format')
            self.weekdays = dt_formats.get(df_name, {}).get('weekdays')
        self.choices = os.stat('expressions.txt')[6] // (6 * 60)
        
    def read(self, offset=0):
        data = self.i2c.readfrom_mem(104, 0, 7)
        def bcd(pos, mask=0xff):
            d = data[pos] & mask
            return (d & 0x0f) + ((d >> 4) * 10)
        s = bcd(0)
        m = bcd(1)
        h = bcd(2, 0x3f)
        w = bcd(3)
        d = bcd(4)
        mm = bcd(5, 0x7f)
        y = bcd(6) + 2000 + (data[5] >> 7) * 100
        t = time.mktime((y, mm, d, h, m, s, w, 0)) + offset
        # adjust by timezone
        if self.tz_data:
            s = f'2022-{mm:02d}-{d:02d}T{h:02d}:{m:02d}:{s:02d}'
            offset = 0
            for k, v in self.tz_data.items():
                if s >= k:
                    offset = v
            t += int(offset * 3600)
        return time.gmtime(t)
    
    def get_strings(self, offset=0):
        y, mm, d, h, m, s, w, dd = self.read(offset)
        with open('expressions.txt') as f:
            f.seek((h * self.choices + random.randint(0, self.choices - 1)) * 6)
            hs = f.read(5)
            f.seek((m * self.choices + random.randint(0, self.choices - 1)) * 6)
            ms = f.read(5)
        hs += 'h'
        ms += 'm'
        ds = ''
        if self.dt_format and self.weekdays:
            ds = self.dt_format
            ds = ds.replace('%d', f'{d:02}')
            ds = ds.replace('%mm', f'{mm:02}')
            ds = ds.replace('%y', f'{y:04}')
            ds = ds.replace('%w', self.weekdays[w])
        return hs, ms, ds
        
    def set_from_epoch(self, epoch):
        data = bytearray(7)
        def bcd(pos, d, bits=0x00):
            b = (d % 10) + (d // 10) * 16 | bits
            data[pos] = b
        gmt = time.gmtime((epoch - 946684800000) // 1000)
        y = gmt[0] - 2000
        y = max(0, y)
        y = min(199, y)
        mm = gmt[1]
        d = gmt[2]
        h = gmt[3]
        m = gmt[4]
        s = gmt[5]
        w = gmt[6] # 0 = Monday
        century = 0x00
        if y > 100:
            y -= 100
            century = 0x80
        bcd(0, s)
        bcd(1, m)
        bcd(2, h)
        bcd(3, w)
        bcd(4, d)
        bcd(5, mm, century)
        bcd(6, y)
        self.i2c.writeto_mem(104, 0, data)
        
def test():
    from time import sleep_ms
    c = Clock('Europe/Berlin')
    c.set_from_epoch(1702383162465)
    for _ in range(10):
        print(c.read())
        sleep_ms(990)

        
        