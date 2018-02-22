import framebuf
import time
from machine import SPI, I2C, Pin


class Display:
    width = 84
    height = 48

    def __init__(self, spi, dc, rst=None, cs=None):
        self._spi = spi
        self._cs = cs or (lambda x: x)
        self._rst = rst or (lambda x: x)
        self._dc = dc
        self._fn = 0x20
        self._buffer = bytearray(504)
        self.fb = framebuf.FrameBuffer(self._buffer, 84, 48,
                                       framebuf.MONO_VLSB)
        self.reset()

    def _command(self, command):
        self._dc(0)
        self._cs(0)
        self._spi.write(command)
        self._cs(1)
        self._dc(1)

    def reset(self):
        self._rst(0)
        time.sleep_us(100)
        self._rst(1)
        time.sleep_us(100)
        self.contrast()
        self.inverse(0)

    def active(self, val):
        if val:
            self._fn &= ~0x04
        else:
            self._fn |= 0x04
        self._command(bytes((self._fn,)))

    def inverse(self, val):
        self._command(b'\x0d' if val else b'\x0c')

    def contrast(self, val=63, bias=20, temp=6):
        if not (0 <= val <= 127 and 16 <= bias <= 23 and 4 <= temp <= 7):
            raise ValueError()
        self._command(bytes((self._fn | 1, temp, bias, 0x80 | val, self._fn)))

    def update(self):
        self._dc(0)
        self._cs(0)
        self._spi.write(b'\x40\x80')
        self._dc(1)
        self._spi.write(self._buffer)
        self._cs(1)


class Backlight:
    def __init__(self, i2c, address=0x0d):
        self._i2c = i2c
        self._address = address

    def color(self, r, g, b):
        data = bytearray((0x6e, r, g, b))
        self._i2c.writeto(self._address, data)


class Buttons:
    UP = 0x80
    LEFT = 0x40
    DOWN = 0x20
    RIGHT = 0x10
    A = 0x08
    B = 0x04
    C = 0x01

    def __init__(self, i2c, address=0x38):
        self._i2c = i2c
        self._address = address

    def get_pressed(self):
        return self._i2c.readfrom(self._address, 1)[0] ^ 0xff


i2c = I2C(-1, sda=Pin(4), scl=Pin(5))
backlight = Backlight(i2c)
buttons = Buttons(i2c)
spi = SPI(1, baudrate=10000000)
display = Display(spi, Pin(2, Pin.OUT, value=1), Pin(0, Pin.OUT, value=0),
                  Pin(15, Pin.OUT, value=1))
