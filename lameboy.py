from machine import SPI, I2C, Pin
import pcd8544


class Backlight:
    def __init__(self, i2c, address=0x0d):
        self._i2c = i2c
        self._address = address

    def color(self, r, g, b):
        data = bytearray((0x6e, r, g, b))
        self._i2c.writeto(self._address, data)


class Buttons:
    def __init__(self, i2c, address=0x38):
        self._i2c = i2c
        self._address = address

    def get_pressed(self):
        return self._i2c.readfrom(self._address, 1)[0]


i2c = I2C(-1, sda=Pin(4), scl=Pin(5))
backlight = Backlight(i2c)
buttons = Buttons(i2c)
spi = SPI(1, baudrate=10000000)
display = pcd8544.Display(spi, Pin(2, Pin.OUT), Pin(0, Pin.OUT),
                          Pin(15, Pin.OUT))
