import clock
import machine
import select
import errno
import time

class Setup:
    
    def __init__(self):
        from random import randint
        self.dtformat = ''
        self.timezone = ''
        self.dtformat, self.timezone = self.read_config()
        self.clock = clock.Clock()
        try:
            with open('password.txt', 'r') as f:
                self.pwd = f.read()
        except:
            self.pwd = ''.join([str(randint(0, 10)) for _ in range(9)])
            with open('password.txt', 'w') as f:
                f.write(self.pwd)
        print(self.pwd)
    
    def read_config(self):
        import ujson
        try:
            with open('config.json', 'r') as f:
                obj = ujson.load(f)
            return (obj.get('df', ''), obj.get('tz', ''))
        except:
            return ('', '')
    
    def write_config(self):
        import ujson
        try:
            timezone, dtformat = self.read_config()
            if timezone != self.timezone or dtformat != self.dtformat:
                obj = {'tz': self.timezone, 'df': self.dtformat}
                with open('config.json', 'w') as f:
                    ujson.dump(obj, f)
        except:
            pass
    
    def show(self):
        import display
        d = display.Display()
        d.text('Calcuclock setup', 400, 50, True)
        d.text('1. Connect to WiFi', 10, 140)
        d.qr(f'WIFI:S:calcuclock;T:WPA;P:{self.pwd};;', 50, 220)
        d.text('2. Open config URL', 410, 140)
        d.qr('http://192.168.4.1', 450, 220)
        d.show()
        d.sleep()
    
    def time_zones(self):
        import os
        for l1 in os.listdir('_zones'):
            if not l1.endswith('.py'):
                for l2 in os.listdir('_zones/' + l1):
                    if l2 != '__init__.py':
                        yield f'{l1}/{l2.replace(".py", "")}'      
    
    def dt_formats(self):
        yield 'English'
        yield 'German'
        
    def html(self):
        yield '<head>'
        yield '<title>Calcuclock setup</title>'
        yield '<meta name="viewport" content="width=device-width, intitial-scale=1" />'
        yield '</head>'
        
        yield '<body>'
        yield '<form>'
        yield '<div style="display: flex; flex-direction: column">'
        yield '<h1>Calcuclock Setup</h1>'
        yield '<h2>Time Zone</h2>'
        yield f'<select name="timezone" id="timezone" style="font-size: 1.5em;">'
        for tz in self.time_zones():
            yield f'<option value="{tz}" {"selected" if tz==self.timezone else ""}>{tz}</option>'
        yield '</select>'
        yield '<h2>Date-Time Format</h2>'
        yield f'<select name="dtformat" id="dtformat" style="font-size: 1.5em;" selected="{self.dtformat}">'
        for df in self.dt_formats():
            yield f'<option value="{df}" {"selected" if df==self.dtformat else ""}>{df}</option>'
        yield '</select>'
        yield '<input type="hidden" id="utc" name="utc" value="">'
        yield '<p />'
        yield '<input type="submit" style="font-size: 1.5em;" value="Synchronize" />'
        yield '</div>'
        yield '</form>'
        yield '</body>'
        
        yield '<script type="text/javascript">'
        yield 'function setTime() {'
        yield 'document.getElementById("utc").value = "" + Date.now();'
        yield 'setTimeout(setTime, 1000);'
        yield '}'
        yield 'setTimeout(setTime, 1000);'
        yield '</script>'
    
    def ok(self):
        yield '<head>'
        yield '<title>Calcuclock setup</title>'
        yield '<meta name="viewport" content="width=device-width, intitial-scale=1" />'
        yield '</head>'
        
        yield '<body>'
        yield '<h1>OK</h1>'
        yield '</body>'
    
    def start_server(self):
        import network as nw
        import usocket as socket
        
        ap = nw.WLAN(nw.AP_IF)
        ap.active(True)
        ap.config(
            essid='calcuclock',
            password=self.pwd,
            authmode=nw.AUTH_WPA2_PSK,
            hidden=False
        )
        while not ap.active():
            pass
        print('AP is active')
        print(ap.ifconfig())
        sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sck.bind(('', 80))
        sck.listen(5)
        while True:
            try:
                conn, addr = sck.accept()
                print(f'Connection from {addr}')
                led = machine.Pin(2, machine.Pin.OUT)
                led.on()
                request = conn.recv(1024)
                print(f'Request: {request}')
                led.off()
                timezone = None
                dtformat = None
                utc = None
                for line in request.split(b'\n'):
                    if not line or line == b'\r\n':
                        break
                    if line.startswith(b'GET') and b'?' in line:
                        line = line.decode('utf-8')
                        for p in line.split(' ')[1].split('?')[1].split('&'):
                            k, v = p.split('=')
                            if k == 'timezone':
                                timezone = v.replace('%2F', '/')
                            if k == 'dtformat':
                                dtformat = v
                            if k == 'utc':
                                utc = int(v)
                print(timezone, dtformat, utc)
                conn.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\nConnection: close\r\n\r\n')
                print('sent 200')
                if timezone and dtformat and utc:
                    self.clock.set_from_epoch(utc)
                    self.timezone = timezone
                    self.dtformat = dtformat
                    self.write_config()
                    for s in self.ok():
                        conn.send(s)
                    break
                else:
                    for s in self.html():
                        conn.send(s)
                print('closing')
                conn.close()
            except Exception as e:
                print(e, type(e).__name__)
            
        time.sleep_ms(900)
        machine.deepsleep(100)

def setup_show():
    setup = Setup()
    setup.show()

def setup_server():
    setup = Setup()
    setup.start_server()
    