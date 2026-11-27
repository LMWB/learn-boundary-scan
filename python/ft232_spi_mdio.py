#!/usr/bin/env python3
"""
mdio_ftdi.py - MDIO (IEEE 802.3 Clause 22) ueber die SPI-Engine (MPSSE) des FT232H.

Gleiches Prinzip wie die STM32-Variante: Ein kompletter 64-Bit-Frame wird in
einem Full-Duplex-SPI-Transfer (Mode 0) gesendet, die Antwort der PHY steht
in den letzten beiden empfangenen Bytes.

Verdrahtung (FT232H Breakout, 3,3 V):
    AD0 (SCK)   ----------------------> MDC
    AD1 (MOSI)  ---[1 kOhm]--+--------> MDIO
                             |
    AD2 (MISO)  -------------+
    AD3 (CS0)   nicht angeschlossen
    GND         ----------------------> GND (gemeinsame Masse!)

    MDIO braucht einen Pull-Up nach VDDIO der PHY (1,5 k bis 2,2 k je nach PHY).
    Auf dem Nucleo-144 ist er bereits vorhanden.

Voraussetzungen:
    pip install pyftdi
    Linux:   udev-Regel fuer VID 0403 / PID 6014, sonst als root starten
    Windows: libusbK-Treiber per Zadig fuer das FT232H-Interface 0

Beispiele:
    python mdio_ftdi.py scan
    python mdio_ftdi.py read 0 2
    python mdio_ftdi.py write 0 0 0x8000        # Reset der PHY
    python mdio_ftdi.py dump 0
    python mdio_ftdi.py mmd-read 1 0x1F 0x0000  # PHY 1, DEVAD 0x1F, Adresse 0x0000
"""

import argparse
import sys

from pyftdi.spi import SpiController


class MdioSpi:
    """MDIO-Master auf Basis eines FT232H im SPI-Modus 0."""

    def __init__(self, url="ftdi://ftdi:232h/1", freq=1_000_000):
        # freq: SCK/MDC in Hz. Standard erlaubt max. 2,5 MHz, viele PHYs mehr.
        self._spi = SpiController()
        self._spi.configure(url)
        self._port = self._spi.get_port(cs=0, freq=freq, mode=0)

    def close(self):
        self._spi.terminate()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def _xfer(self, tx):
        """Full-Duplex-Transfer, gibt genauso viele Bytes zurueck wie gesendet."""
        return bytes(self._port.exchange(tx, len(tx), duplex=True))

    # ---- Clause 22 -------------------------------------------------------

    def read(self, phy, reg):
        """Liest ein 16-Bit-Register (reg 0..31) der PHY mit Adresse phy (0..31)."""
        phy &= 0x1F
        reg &= 0x1F
        tx = bytes([
            0xFF, 0xFF, 0xFF, 0xFF,                          # Preamble
            0x60 | (phy >> 1),                               # ST=01, OP=10, PHYAD[4:1]
            ((phy & 1) << 7) | (reg << 2) | 0x03,            # PHYAD[0], REGAD, TA (Master laesst los)
            0xFF, 0xFF,                                      # Datenphase: Bus freigeben
        ])
        rx = self._xfer(tx)
        return (rx[6] << 8) | rx[7]

    def write(self, phy, reg, value):
        """Schreibt ein 16-Bit-Register."""
        phy &= 0x1F
        reg &= 0x1F
        value &= 0xFFFF
        tx = bytes([
            0xFF, 0xFF, 0xFF, 0xFF,
            0x50 | (phy >> 1),                               # ST=01, OP=01, PHYAD[4:1]
            ((phy & 1) << 7) | (reg << 2) | 0x02,            # PHYAD[0], REGAD, TA=10
            value >> 8, value & 0xFF,
            0xFF,                                            # MDIO nach dem Frame sicher loslassen
        ])
        self._xfer(tx)

    # ---- Erweiterte Register (MMD-indirekt ueber REGCR 0x0D / ADDAR 0x0E) --

    def mmd_read(self, phy, devad, addr):
        self.write(phy, 0x0D, devad & 0x1F)                  # Funktion: Adresse
        self.write(phy, 0x0E, addr & 0xFFFF)
        self.write(phy, 0x0D, 0x4000 | (devad & 0x1F))       # Funktion: Daten, ohne Post-Increment
        return self.read(phy, 0x0E)

    def mmd_write(self, phy, devad, addr, value):
        self.write(phy, 0x0D, devad & 0x1F)
        self.write(phy, 0x0E, addr & 0xFFFF)
        self.write(phy, 0x0D, 0x4000 | (devad & 0x1F))
        self.write(phy, 0x0E, value & 0xFFFF)

    # ---- Hilfsfunktionen -------------------------------------------------

    def scan(self):
        """Gibt eine Liste (adresse, id1, id2) aller antwortenden PHYs zurueck."""
        found = []
        for a in range(32):
            id1 = self.read(a, 2)
            if id1 != 0xFFFF:
                found.append((a, id1, self.read(a, 3)))
        return found


def _int(s):
    return int(s, 0)  # akzeptiert 10, 0x0A, 0b1010


def main():
    p = argparse.ArgumentParser(description="MDIO ueber FT232H (SPI-Modus)")
    p.add_argument("--url", default="ftdi://ftdi:232h/1", help="pyftdi-URL des Adapters")
    p.add_argument("--freq", type=_int, default=1_000_000, help="MDC in Hz (Standard: 1 MHz)")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("scan", help="alle 32 Adressen nach PHYs absuchen")

    r = sub.add_parser("read", help="Register lesen")
    r.add_argument("phy", type=_int)
    r.add_argument("reg", type=_int)

    w = sub.add_parser("write", help="Register schreiben")
    w.add_argument("phy", type=_int)
    w.add_argument("reg", type=_int)
    w.add_argument("value", type=_int)

    d = sub.add_parser("dump", help="Register 0..31 ausgeben")
    d.add_argument("phy", type=_int)

    mr = sub.add_parser("mmd-read", help="erweitertes Register lesen")
    mr.add_argument("phy", type=_int)
    mr.add_argument("devad", type=_int)
    mr.add_argument("addr", type=_int)

    mw = sub.add_parser("mmd-write", help="erweitertes Register schreiben")
    mw.add_argument("phy", type=_int)
    mw.add_argument("devad", type=_int)
    mw.add_argument("addr", type=_int)
    mw.add_argument("value", type=_int)

    args = p.parse_args()

    with MdioSpi(args.url, args.freq) as mdio:
        if args.cmd == "scan":
            found = mdio.scan()
            if not found:
                print("Keine PHY gefunden (alle Adressen lieferten 0xFFFF).")
                return 1
            for a, id1, id2 in found:
                print(f"PHY @{a}: ID1=0x{id1:04X} ID2=0x{id2:04X}")
        elif args.cmd == "read":
            print(f"0x{mdio.read(args.phy, args.reg):04X}")
        elif args.cmd == "write":
            mdio.write(args.phy, args.reg, args.value)
        elif args.cmd == "dump":
            for reg in range(32):
                print(f"reg {reg:2d} (0x{reg:02X}) = 0x{mdio.read(args.phy, reg):04X}")
        elif args.cmd == "mmd-read":
            print(f"0x{mdio.mmd_read(args.phy, args.devad, args.addr):04X}")
        elif args.cmd == "mmd-write":
            mdio.mmd_write(args.phy, args.devad, args.addr, args.value)
    return 0


if __name__ == "__main__":
    sys.exit(main())
