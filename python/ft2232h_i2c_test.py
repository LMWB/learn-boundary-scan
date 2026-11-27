'''
Beim FT2232H gibt es zwei unabhängige Kanäle (A und B), die beide MPSSE können. Dein JTAG liegt auf ADBUS0 bis 3 (Kanal A), also nimmst du für I2C einfach Kanal B. Beide laufen dann parallel, ohne sich zu stören.

Pinout für I2C auf Kanal B:

Pin         Signal      Hinweis
BDBUS0	    SCL	
BDBUS1	    SDA (out)
BDBUS2	    SDA (in)    mit BDBUS1 verbinden (Brücke)
GND	        GND	        gemeinsame Masse

Alternative mit Serien Widerstand <1kOhm um mit MDIO (SPI) compatible

BDBUS0 ----------------------> SCL	
BDBUS1 ---[1 kOhm]--+--------> SDA (out)
                    |
BDBUS1 -------------+          SDA (in)    mit BDBUS1 verbinden
GND    ----------------------> GND	    gemeinsame Masse


'''
from pyftdi.i2c import I2cController

i2c = I2cController()
i2c.configure('ftdi://ftdi:2232h/2', frequency=100000)   # /2 = Kanal B

print("Scanne I2C-Bus...")
devices = []
for addresse in range(0x08, 0x78):
    port = i2c.get_port(addresse)
    try:
        port.read(0)          # reiner Adress-Check (ACK?)
        devices.append(addresse)
    except Exception:
        pass

if devices:
    for a in devices:
        print(f"Gerät gefunden bei 0x{a:02X}")
else:
    print("Keine Geräte gefunden")

i2c.terminate()