from pyftdi.gpio import GpioAsyncController

# ASSUMED wiring: BDBUS0 = SER, BDBUS1 = SRCLK, BDBUS2 = RCLK. Change to match your board.
SER, SRCLK, RCLK = 0x01, 0x02, 0x04

gpio = GpioAsyncController()
gpio.configure('ftdi://ftdi:2232h/2', direction=SER | SRCLK | RCLK)  # /2 = channel B

def send(byte):
    for i in range(7, -1, -1):             # MSB first
        bit = SER if (byte >> i) & 1 else 0
        gpio.write(bit)                    # set data, clock low
        gpio.write(bit | SRCLK)            # clock high: bit shifts in
        gpio.write(bit)                    # clock low
    gpio.write(RCLK)                       # latch pulse: LEDs update
    gpio.write(0)

send(0x00)    # all LEDs off; use 0xFF if your LEDs are wired active-low
gpio.close()