testing flashing the 250kByte bin file results in very longe execution time

```tcl
lmwb@macbookpro12:~/work/git/LMWB/learn-boundary-scan/python$ /bin/python3 /home/lmwb/work/git/LMWB/learn-boundary-scan/python/flash_bin_openOCD.py
Open On-Chip Debugger 0.12.0
Licensed under GNU GPL v2
For bug reports, read
	http://openocd.org/doc/doxygen/bugs.html
Info : only one transport option; autoselect 'jtag'
none separate

Info : usb blaster interface using libftdi
Info : This adapter doesn't support configurable speed
Info : JTAG tap: stm32f4x.cpu tap/device found: 0x4ba00477 (mfg: 0x23b (ARM Ltd), part: 0xba00, ver: 0x4)
Info : JTAG tap: stm32f4x.bs tap/device found: 0x06421041 (mfg: 0x020 (STMicroelectronics), part: 0x6421, ver: 0x0)
Info : JTAG tap: max10.tap tap/device found: 0x031820dd (mfg: 0x06e (Altera), part: 0x3182, ver: 0x0)
Info : [stm32f4x.cpu] Cortex-M4 r0p1 processor detected
Info : [stm32f4x.cpu] target has 6 breakpoints, 4 watchpoints
Info : starting gdb server for stm32f4x.cpu on 3333
Info : Listening on port 3333 for gdb connections
Error: Translation from khz to adapter speed not implemented
Error executing event reset-start on target stm32f4x.cpu:

Info : JTAG tap: stm32f4x.cpu tap/device found: 0x4ba00477 (mfg: 0x23b (ARM Ltd), part: 0xba00, ver: 0x4)
Info : JTAG tap: stm32f4x.bs tap/device found: 0x06421041 (mfg: 0x020 (STMicroelectronics), part: 0x6421, ver: 0x0)
Info : JTAG tap: max10.tap tap/device found: 0x031820dd (mfg: 0x06e (Altera), part: 0x3182, ver: 0x0)
[stm32f4x.cpu] halted due to debug-request, current mode: Thread 
xPSR: 0x01000000 pc: 0x08000910 msp: 0x20020000
Error: Translation from khz to adapter speed not implemented
Error executing event reset-init on target stm32f4x.cpu:

** Programming Started **
Info : device id = 0x10006421
Info : flash size = 512 KiB
** Programming Finished **
** Verify Started **
** Verified OK **
** Resetting Target **
Error: Translation from khz to adapter speed not implemented
Error executing event reset-start on target stm32f4x.cpu:

Info : JTAG tap: stm32f4x.cpu tap/device found: 0x4ba00477 (mfg: 0x23b (ARM Ltd), part: 0xba00, ver: 0x4)
Info : JTAG tap: stm32f4x.bs tap/device found: 0x06421041 (mfg: 0x020 (STMicroelectronics), part: 0x6421, ver: 0x0)
Info : JTAG tap: max10.tap tap/device found: 0x031820dd (mfg: 0x06e (Altera), part: 0x3182, ver: 0x0)
shutdown command invoked
binary size:  265364 bytes (259.1 KiB)
time elapsed: 406.877 s
throughput:   0.6 KiB/s
lmwb@macbookpro12:~/work/git/LMWB/learn-boundary-scan/python$ 
```
