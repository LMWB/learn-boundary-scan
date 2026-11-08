# learn-boundary-scan
JTAG and Boundary Scan Basics with low price Hardware 

## Things you need  
![max1000](./docs/images/MAX1000-pinout.png)  
![max1000-LED](./docs/images/MAX1000-LED-Bank.png)  
![nucleof446re](./docs/images/nucleo-f446re-pinout.svg)  
![ft2232-board](./docs/images/ft2232h-dev-board.jpg)  
[on ebay](https://www.ebay.de/itm/265993756736?_skw=ft2232&itmmeta=01M6PQ0XWMB1DCS2C043ZNTX8C&hash=item3dee76a040:g:ddoAAOSwdHRjdZys&itmprp=enc%3AAQALAAAA8CHNgUiiE%2FjQhlDTaMiAde8UnivYtuuf1oo0AGURx0LGN%2BPUHMYM9LpCCYqT6sVC05qNus3w0SfR1J8Er3rfPLJST7wkwdx6DOlTNgtWLjMvifUuh0On9n5vwOR23Zt8S6CO0odvclKxGXhHJHVkZoldgRPFiufyJ2ofRDoujkWGcWqq6xkG1juugf0%2FNQJV0Iur%2BqGlS0hpLTzJIhLRS0I3sA9SLwMuzMCWJ5hKvit0hYqj%2BIHlDJyXTNiVfRq4RGt3ByYGAxM8cHjvVQ1IV9iG48PRqaTp3DxWS1lc52nH%2BsR%2F2GMNtrwdQJjcl51qvw%3D%3D%7Ctkp%3ABk9SR6bfg9e1aA)  

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

## Select a part and read its IDCODE directly  
```
part 0
instruction IDCODE
shift ir
shift dr
dr
```

## scripting  

```
cable ft2232 vid=0x0403 pid=0x6010 interface=0
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

Then run it with jtag led.jtag, or from inside UrJTAG with script led.jtag. 

include led.urjtag. 

Put a usleep between steps if you want the LED to stay on visibly before the release.
