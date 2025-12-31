#!/bin/bash

kicad-cli pcb export svg --layers Edge.Cuts --exclude-drawing-sheet --drill-shape-opt 0 -o case/build/pcb_outline.svg pcb/pcb.kicad_pcb
kicad-cli pcb export svg --layers User.1 --exclude-drawing-sheet --drill-shape-opt 0 -o case/build/switch_holes.svg pcb/pcb.kicad_pcb
kicad-cli pcb export svg --layers User.2 --exclude-drawing-sheet --drill-shape-opt 0 -o case/build/mounting_holes.svg pcb/pcb.kicad_pcb
kicad-cli pcb export svg --layers User.3 --exclude-drawing-sheet --drill-shape-opt 0 -o case/build/extras_left.svg pcb/pcb.kicad_pcb
kicad-cli pcb export svg --layers User.4 --exclude-drawing-sheet --drill-shape-opt 0 -o case/build/extras_right.svg pcb/pcb.kicad_pcb
