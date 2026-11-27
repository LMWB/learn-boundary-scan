'''
Pinout für I2C (FT232H, Port AD):

Signal	    Pin am Board	FT232H
SCL	        AD0	            ADBUS0
SDA (out)	AD1	            ADBUS1
SDA (in)	AD2	            ADBUS2
GND	        GND             –
'''


from pyftdi.i2c import I2cController

i2c = I2cController()
i2c.configure('ftdi://ftdi:232h/1', frequency=100000)   # Standard-URL für den FT232H

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