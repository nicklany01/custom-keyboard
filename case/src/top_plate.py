from build123d import *
from ocp_vscode import show

svg_wires = import_svg("case/build/pcb_outline.svg")
pcb_face = make_face(svg_wires)

with BuildPart() as case:
    add(pcb_face)
    extrude(amount=2)

show(case)
