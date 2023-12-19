import machine
import time
from lib.writer import writer
import framebuf
import arial_40
from array import array

class DisplayFrameBuffer(framebuf.FrameBuffer):

    def __init__(self, buf, width, height, *args, **kwargs):
        self.width = width
        self.height = height
        super().__init__(buf, width, height, *args, **kwargs)
        
class Display:

    def __init__(self):
        self.width = 800
        self.height = 480
        self.buf = bytearray(self.width * self.height // 8)
        self.fb = DisplayFrameBuffer(self.buf, self.width, self.height, framebuf.MONO_HLSB)
        self.writer = writer.Writer(self.fb, arial_40)
        self.busy_pin = machine.Pin(25, machine.Pin.IN)
        self.rst_pin = machine.Pin(26, machine.Pin.OUT)
        self.dc_pin = machine.Pin(27, machine.Pin.OUT)
        self.cs_pin = machine.Pin(9, machine.Pin.OUT)
        self.pwr_pin = machine.Pin(10, machine.Pin.OUT)
        self.clk_pin = machine.Pin(18, machine.Pin.OUT)
        self.din_pin = machine.Pin(23, machine.Pin.OUT)
        self.spi = machine.SPI(2, baudrate=2_000_000, sck=self.clk_pin, mosi=self.din_pin)
        self.char_width = 96
        self.char_height = 150
        self.char_spacing = 120 - self.char_width
        self.on()
        self.reset()
        self.init()

    def on(self):
        self.pwr_pin.on()

    def off(self):
        time.sleep_ms(20)
        self.pwr_pin.off()

    def reset(self):
        self.rst_pin.off()
        time.sleep_ms(4)
        self.rst_pin.on()
        time.sleep_ms(200)
    
    def wait(self, sleep_before=None):
        if sleep_before:
            time.sleep_ms(sleep_before)
        while not self.busy_pin.value():
            time.sleep_ms(20)

    def command(self, command, data=None):
        self.cs_pin.off()
        self.dc_pin.off()
        self.spi.write(command)
        if data:
            self.dc_pin.on()
            self.spi.write(data)
        self.cs_pin.on()

    def init(self):
        self.command(b'\x01', b'\x07\x07\x3f\x3f')
        self.command(b'\x04')
        self.wait(100)
        self.command(b'\x00', b'\x1f')
        self.command(b'\x61', b'\x03\x20\x01\xe0')
        self.command(b'\x15', b'\x00')
        self.command(b'\x50', b'\x10\x07')
        self.command(b'\x60', b'\x22')
        self.wait()

    def show(self):
        self.command(b'\x13', self.buf)
        self.command(b'\x12')
        self.wait(100)

    def sleep(self):
        self.command(b'\x02')
        self.wait()
        self.command(b'0x07', b'0xa5')
        time.sleep_ms(2000)
        self.off()
        self.fb = None
        self.buf = None

    def text(self, s, x, y, center=False):
        w = self.writer.stringlen(s)
        if center:
            x -= w // 2
        self.writer.set_textpos(self.fb, y, x)
        self.writer.printstring(s)
    
    def big_text(self, line, x, y):
        line = line.replace('*', 'x')
        line = line.replace('/', 'd')
        for c in line:
            with open(c + '.buf', 'rb') as f:
                char_buf = bytearray(f.read())
            char_fb = framebuf.FrameBuffer(char_buf, self.char_width, self.char_height, framebuf.MONO_HLSB)
            self.fb.blit(char_fb, x, y)
            x += self.char_width + self.char_spacing
    
    @micropython.native
    def qr(self, s, left, top, bs = 4):
        from lib.uqr.uQR import QRCode
        qr = QRCode()
        qr.add_data(s, 0)
        matrix = qr.get_matrix()
        for y in range(len(matrix)):
            for x in range(len(matrix[y])):
                col = 1 if matrix[y][x] else 0
                x1 = left + x * bs
                y1 = top + y * bs
                x2 = x1 + bs - 1
                y2 = y1 + bs - 1 
                self.fb.fill_rect(x1, y1, x2, y2, col)
    
    def draw_battery(self, x, y, cap, loading, drained, bs=1):
        self.fb.fill_rect(x - 10 * bs, y - 5 * bs, 1 * bs, 10 * bs, 1)
        self.fb.fill_rect(x + 9 * bs, y - 5 * bs, 1 * bs, 10 * bs, 1)
        self.fb.fill_rect(x - 10 * bs, y - 5 * bs, 20 * bs, 1 * bs, 1)
        self.fb.fill_rect(x - 10 * bs, y + 4 * bs, 20 * bs, 1 * bs, 1)
        self.fb.fill_rect(x - 12 * bs, y - 2 * bs, 2 * bs, 4 * bs, 1)
        if loading:
            self.fb.fill_rect(x - 2 * bs, y - 3 * bs, 4 * bs, 6 * bs, 1)
            self.fb.fill_rect(x - 3 * bs, y - 2 * bs, 1 * bs, 4 * bs, 1)
            self.fb.fill_rect(x + 2 * bs, y - 2 * bs, 3 * bs, 1 * bs, 1)
            self.fb.fill_rect(x + 2 * bs, y + 1 * bs, 3 * bs, 1 * bs, 1)
            self.fb.fill_rect(x - 6 * bs, y - 1 * bs, 3 * bs, 2 * bs, 1)
        elif drained:
            self.fb.poly(x - 4 * bs, y - 3 * bs, array('h', [
                0 * bs, 6 * bs,
                6 * bs, 0 * bs,
                8 * bs, 0 * bs,
                2 * bs, 6 * bs,
                0 * bs, 6 * bs
            ]), 1, True)
        else:
            o = round((100 - cap) / 100 * 16 * bs)
            self.fb.fill_rect(x - 8 * bs + o, y - 3 * bs, 16 * bs - o, 6 * bs, 1)

                   
def test():
    display = Display()
    display.text('Hello world', 10, 10)
    display.big_text('1+2*3', 10, 60)
    display.qr('http://www.heise.de', 10, 300)
    display.show()
    display.sleep()

def clear():
    display = Display()
    display.show()
    display.sleep()
    