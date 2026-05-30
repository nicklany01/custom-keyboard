#!/usr/bin/env bash

kicad-cli pcb export svg --layers Edge.Cuts --exclude-drawing-sheet --drill-shape-opt 0 -o case/build/pcb_outline.svg pcb/pcb.kicad_pcb
kicad-cli pcb export svg --layers User.Mounting_Holes --exclude-drawing-sheet --drill-shape-opt 0 -o case/build/mounting_holes.svg pcb/pcb.kicad_pcb
kicad-cli pcb export svg --layers User.Plate_Cutout --exclude-drawing-sheet --drill-shape-opt 0 -o case/build/plate_cutout.svg pcb/pcb.kicad_pcb
kicad-cli pcb export svg --layers User.Top_Edge --exclude-drawing-sheet --drill-shape-opt 0 -o case/build/top_edge.svg pcb/pcb.kicad_pcb
kicad-cli pcb export svg --layers User.Top_Cutout --exclude-drawing-sheet --drill-shape-opt 0 -o case/build/top_cutout.svg pcb/pcb.kicad_pcb
kicad-cli pcb export svg --layers User.Extras_Left --exclude-drawing-sheet --drill-shape-opt 0 -o case/build/extras_left.svg pcb/pcb.kicad_pcb
kicad-cli pcb export svg --layers User.Extras_Right --exclude-drawing-sheet --drill-shape-opt 0 -o case/build/extras_right.svg pcb/pcb.kicad_pcb
