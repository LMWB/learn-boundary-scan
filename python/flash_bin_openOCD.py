import os
import time

here = os.path.dirname(os.path.abspath(__file__))
cfg = os.path.join(here, "..", "openOCD", "chain.cfg")

#binfile = os.path.join(here, "..", "binaries", "Nucleo-F446RE-blinky_slow.bin")
binfile = os.path.join(here, "..", "binaries", "Nucleo-F446RE-blinky_fast.bin")

size = os.path.getsize(binfile)

tic = time.perf_counter()
os.system(f'openocd -f "{cfg}" -c "program \\"{binfile}\\" 0x8000000 verify reset exit"')
toc = time.perf_counter()

print(f"binary size:  {size} bytes ({size / 1024:.1f} KiB)")
print(f"time elapsed: {toc - tic:.3f} s")
print(f"throughput:   {size / 1024 / (toc - tic):.1f} KiB/s")