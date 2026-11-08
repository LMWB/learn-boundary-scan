# OpenOCD Configuration for the STM32 + MAX 10 JTAG Chain

2026-11-08

## Overview

The config file tells OpenOCD which adapter to use and which devices sit in the JTAG chain, because JTAG offers no way to discover either. It is read again on every start.

Physical wiring, in signal order:

1. FT2232H adapter, TDO out
2. STM32F446 boundary-scan TAP (Nucleo PA15 = TDI)
3. STM32F446 Cortex-M4 debug TAP (Nucleo PB3 = TDO)
4. MAX 10 on the MAX1000 board (TDI in, TDO out)
5. FT2232H adapter, TDI in

OpenOCD numbers the TAPs from the return end, so they are named `max10.tap`, `stm32f4x.cpu` and `stm32f4x.bs`, in that order.

## The config file

The working file, with a comment on each line. The order matters, as explained below.

```tcl
# --- 1. Adapter (the FT2232H board) ---
adapter driver ftdi                   ;# use the FTDI/MPSSE driver
ftdi vid_pid 0x0403 0x6010            ;# USB IDs of an FT2232H
ftdi channel 0                        ;# channel A (ADBUS0-3)
ftdi layout_init 0x0008 0x000b        ;# initial pin levels, pin directions
transport select jtag                 ;# talk JTAG (not SWD)

# --- 2. Chain description ---
# MAX 10 sits in the chain too, so OpenOCD must know it
jtag newtap max10 tap -irlen 10 -expected-id 0x031820DD
source [find target/stm32f4x.cfg]     ;# declares both STM32 TAPs and the core

# --- 3. Overrides (must come after the target file) ---
adapter speed 1000                    ;# TCK = 1 MHz
reset_config none                     ;# no reset wires connected
```

## Adapter lines

These five lines describe the FT2232H board and how its pins map to JTAG signals.

| Line | What it does |
| --- | --- |
| `adapter driver ftdi` | Selects the driver for the adapter. The `ftdi` driver uses the FT2232H's MPSSE engine to generate the JTAG signals in hardware. Older OpenOCD versions call this command `interface`. |
| `ftdi vid_pid 0x0403 0x6010` | Picks the USB device by vendor ID (0x0403 = FTDI) and product ID (0x6010 = FT2232C/D/H). With two identical adapters attached, add `ftdi serial <number>` to choose one. |
| `ftdi channel 0` | Selects channel A of the dual-channel chip (ADBUS0-3, where the JTAG wires are). Channel B would be `1`. UrJTAG's `interface=1` means the same channel, since it counts from 1. |
| `ftdi layout_init 0x0008 0x000b` | Sets the low-byte pins (ADBUS0-7) when the adapter is opened: first value = initial output levels, second = direction mask (1 = output). See the pin table below. |
| `transport select jtag` | Chooses JTAG instead of SWD. The STM32F4 and the FT2232H both support SWD, so OpenOCD has to be told. Boundary scan needs JTAG anyway. |

Pin assignment behind `ftdi layout_init`:

| ADBUS bit | Signal | Direction | Initial level |
| --- | --- | --- | --- |
| 0 | TCK | output | low |
| 1 | TDI (to target) | output | low |
| 2 | TDO (from target) | input | n/a |
| 3 | TMS | output | high (idle level) |

`0x000b` is binary `1011`: bits 0, 1 and 3 are outputs. `0x0008` sets only bit 3 (TMS) high. Without this line OpenOCD would not know which FTDI pin carries which JTAG signal. If NRST is wired later, an `ftdi layout_signal nSRST ...` line is added as well.

## Chain description lines

OpenOCD must know every TAP in the chain and its instruction-register (IR) length, because an instruction for one device has to pass through the IRs of all the others.

| Line | What it does |
| --- | --- |
| `jtag newtap max10 tap -irlen 10 -expected-id 0x031820DD` | Declares one TAP, named `max10.tap`, with a 10-bit IR. At start-up OpenOCD checks that the device reports this IDCODE and stops with an error on a mismatch, which catches wiring mistakes. If the line were missing, every instruction would land at the wrong bit offset. |
| `source [find target/stm32f4x.cfg]` | Loads OpenOCD's built-in script for STM32F4. As far as I know, it declares the two STM32 TAPs (`stm32f4x.cpu`, IR length 4, and `stm32f4x.bs`, IR length 5), creates the Cortex-M4 target and GDB server (port 3333), defines the flash bank at 0x08000000 plus a RAM work area, and sets default clock speed and reset behavior. `find` searches OpenOCD's scripts directory. |

**Order matters.** TAPs are chained in the order they are declared, starting at the device closest to the adapter's TDI return line. The MAX 10 is physically last in the chain, so its `newtap` line must come before the `source` line. The result is the numbering `scan_chain` shows: `max10.tap`, `stm32f4x.cpu`, `stm32f4x.bs`.

The IDCODEs seen on this setup:

| TAP | IDCODE | IR length |
| --- | --- | --- |
| `max10.tap` | 0x031820DD | 10 |
| `stm32f4x.cpu` (Cortex-M4 debug) | 0x4BA00477 | 4 |
| `stm32f4x.bs` (boundary scan) | 0x06421041 | 5 |

## Override lines

Both lines must come after the `source` line, because the target file sets its own defaults and the last setting wins.

| Line | What it does |
| --- | --- |
| `adapter speed 1000` | Sets the TCK frequency to 1000 kHz (1 MHz). The target file's default is 2000 kHz, which was visible in the first run's log. 1 MHz is a safe choice for hand-wired jumpers across three boards; the FT2232H itself can go much faster. |
| `reset_config none` | Tells OpenOCD that no reset lines (nTRST, nSRST) are wired from the adapter. It then resets through the JTAG state machine and, for the core, through a software reset request. That is why `reset halt` works without an NRST wire. |

If NRST is wired later, replace `reset_config none` with a setting that matches the wiring (for example `srst_only`) and define the pin with `ftdi layout_signal nSRST`. A pin reset is more thorough than the software reset.

## Why it is needed on every call

OpenOCD keeps no memory between runs. Each call starts a new process that reads the config, opens the USB adapter, scans the chain and then exits when its commands finish. The chips keep their own state (flash contents, a halted core), but OpenOCD's knowledge of the hardware is gone each time.

To avoid typing `-f chain.cfg` every time, rename the file to `openocd.cfg`. When OpenOCD is started without `-f`, it looks for that file name in the current directory, so this works:

```bash
openocd -c "init; reset halt; exit"
```

Common calls with the config:

| Task | Command |
| --- | --- |
| Check the chain | `openocd -f chain.cfg -c "init; scan_chain; exit"` |
| Probe the flash | `openocd -f chain.cfg -c "init; reset halt; flash probe 0; flash info 0; exit"` |
| Program an image | `openocd -f chain.cfg -c "program firmware.elf verify reset exit"` |
| Program a raw binary | `openocd -f chain.cfg -c "program firmware.bin 0x08000000 verify reset exit"` |
