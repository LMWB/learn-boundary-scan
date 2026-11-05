# learn-boundary-scan
JTAG and Boundary Scan Basics with low price Hardware 

## Things you need  
![max1000](./docs/images/MAX1000-pinout.png)  
![max1000-LED](./docs/images/MAX1000-LED-Bank.png)  
![nucleof446re](./docs/images/nucleo-f446re-pinout.svg)  
![max1000-LED](./docs/images/ft2232h-dev-board.jpg)  

Some bread board wires. Pullups would be nice but it works without them too.  

## Setup  
![jtag-chain](./docs/images/jtag-chain.png)  
[XJTAG](https://www.youtube.com/watch?v=PgUmq32-HO4)  

## Software  
UrJTAG CLI based Software
[UrJTAG](https://urjtag.sourceforge.io/)  

```
sudo apt install openwince-jtag  
sudo apt install urjtag  
sudo apt install openocd  
```

```
lmwb@macbookpro12:~/work/git/LMWB$ jtag -v

UrJTAG 2021.03 #

Copyright (C) 2002, 2003 ETC s.r.o.
Copyright (C) 2007, 2008, 2009 Kolja Waschk and the respective authors

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
```

## cableing the FT2232H board  
JTAG pin mapping (channel A, MPSSE default)

| JTAG signal | FT2232H pin |
| --- | --- |
| TCK	| ADBUS0 |
| TDI	| ADBUS1 |
| TDO	| ADBUS2 |
| TMS	| ADBUS3 |
| GND	| any GND pin |

## first test  
```
cable ft2232 vid=0x0403 pid=0x6010 interface=1
detect
```

## minimal workflow  
```
cable ft2232 vid=0x0403 pid=0x6010 #cable <your adapter>   # depends on FTDI pinout, e.g. jtagkey

bsdl path /path/to/bsdl_folder
detect
part 0                 # the boundary-scan TAP
instruction SAMPLE/PRELOAD
shift ir
shift dr
set signal PA5 out 1
instruction EXTEST
shift ir
shift dr               # LED turns on
set signal PA5 out 0
shift dr               # LED turns off
```

### Select a part and read its IDCODE directly  
```
part 0
instruction IDCODE
shift ir
shift dr
dr
```

### scripting  

```
cable ft2232 vid=0x0403 pid=0x6010 interface=1
bsdl path /path/to/bsdl_folder
detect
part 0
instruction SAMPLE/PRELOAD
shift ir
shift dr
set signal PA5 out 1
instruction EXTEST
shift ir
shift dr
instruction BYPASS
shift ir
reset
```

Then run it with jtag led.jtag, or from inside UrJTAG with script led.jtag. Put a sleep between steps if you want the LED to stay on visibly before the release.