import os
import math
import glob
import shapely.geometry as sg

from pcbflow import *
from skidl import *


if __name__ == "__main__":
    ###
    ### SKiDL Circuit Declarations
    ###

    # Declare microcontroller
    mcu = Part(
        "DSP_Microchip_DSPIC33",
        "DSPIC33EP256MU806-xPT",
        footprint="TQFP-64_10x10mm_P0.5mm",
    )
    # Declare a generic 0603 capacitor
    cap = Part(
        "Device",
        "C",
        footprint="C_0603_1608Metric_Pad1.08x0.95mm_HandSolder",
        dest=TEMPLATE,
    )
    # Declare 3 instances of our generic capacitor with values
    c1 = cap(value="10uF")
    c2 = cap(value="0.1uF")
    c3 = cap(value="0.1uF")

    # Create GND and VDD nets
    vdd = Net("VDD")
    gnd = Net("GND")

    # Assign VDD and GND to our parts
    mcu["VDD"] += vdd
    mcu["VSS"] += gnd
    for c in [c1, c2, c3]:
        c[1] += vdd
        c[2] += gnd

    ###
    ### pcbflow PCB Declarations
    ###

    # Create a pcbflow Board instance
    brd = Board((55, 30))
    
    # add two inner copper layers (named GP2, GP3)
    brd.add_inner_copper_layer(2)
    # Place 2 mm mounting holes in the corners
    holes = ((5, 5), (5, 25), (50, 5), (50, 25))
    for hole in holes:
        brd.add_hole(hole, 2.0)
    # Add some text (silkscreen on the top), as copper on the bottom
    brd.add_text((10, 25), "Made with pcbflow", justify="left")
    brd.add_text((10, 25), "Made with pcbflow", layer="GBL", keepout_box=True, justify="left")

    # Place a VDD patch under MCU on layer GP3
    brd.add_named_rect((27, 25), (45, 5), layer="GP3", name="VDD")

    # Assign a convenient reference to the default SKiDL circuit
    ckt = default_circuit

    print("Circuit:  Parts: %d  Nets: %d" % (len(ckt.parts), len(ckt.nets)))

    # Assign part locations (we're adding an extra atrribute to the skidl.Part object)
    mcu.loc = (35, 15)
    c1.loc = (25,15)
    c2.loc = (45,15)
    c3.loc = (37,6.5)
    sides = ["top", "bottom", "top", "bottom"]

    # Instantiate SkiPart(PCBPart) instances
    for part, side in zip(ckt.parts, sides):
        sp = SkiPart(brd.DC(part.loc), part, side=side)
        # "fanout" GND and VDD vias from parts with GND and VDD net connections
        sp.fanout(["VDD"])
        sp.fanout(["GND"], relative_to="inside")

    print(brd.parts_str())
    
    # finish the PCB with an outline and poured copper layers
    brd.add_outline()
    brd.fill_layer("GTL", "GND")
    brd.fill_layer("GBL", "GND")
    brd.fill_layer("GP3", "GND")

    # Save the rendered PCB to asset files 
    brd.save("%s" % (__file__[:-3]))