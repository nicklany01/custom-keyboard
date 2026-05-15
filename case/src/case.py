import argparse
from build123d import *
from ocp_vscode import show

TILT_ANGLE = 10
TILT_Z = -14
FLOOR_THICKNESS = 2

WALL_THICKNESS = 2
WALL_HEIGHT = 10

PLATFORM_Z = -4
PLATFORM_THICKNESS = 2

PILLAR_BASE_HEIGHT = 2
PILLAR_BASE_OFFSET = 2
PILLAR_TOP_HEIGHT = 4
PILLAR_TOP_OFFSET = 0.5
HOLE_RAD = 0.8
HOLE_DEPTH = 4

CUTOUT_W = 55
CUTOUT_H = 15
CUTOUT_D = 10.0
CUTOUT_LOC = Pos(140, 110, PLATFORM_Z) * Rot(0, 0, 90)
CUTOUT_ALIGN = (Align.MIN, Align.CENTER, Align.MAX)

VIS_COLOR = Color(1.0, 0.0, 0.0, alpha=0.3)


def main():
    parser = argparse.ArgumentParser(description="Generate case STL.")
    parser.add_argument("--side", nargs="?", default="left", choices=["left", "right"])
    parser.add_argument("--show", action=argparse.BooleanOptionalAction, default=False)
    args = parser.parse_args()

    pcb_wires = import_svg("case/build/pcb_outline.svg")
    hole_wires = import_svg("case/build/mounting_holes.svg")

    hole_wires.sort(key=lambda w: w.center().X)
    hole_wires = hole_wires[:6]

    pcb_face = make_face(pcb_wires)
    hole_faces = [make_face(w) for w in hole_wires]
    hole_locs = [f.bounding_box().center() for f in hole_faces]

    with BuildPart() as base:
        # Tilt logic
        cx = pcb_face.bounding_box().center().X
        tilt_loc = Pos(cx, 0, TILT_Z) * Rot(0, TILT_ANGLE, 0)

        with BuildPart(mode=Mode.PRIVATE) as target_builder:
            with Locations(tilt_loc):
                Box(1000, 1000, 1000, align=(Align.CENTER, Align.CENTER, Align.MAX))
        floor_target = target_builder.part

        with BuildPart(mode=Mode.PRIVATE) as limit_builder:
            with Locations(tilt_loc * Pos(0, 0, FLOOR_THICKNESS)):
                Box(1000, 1000, 1000, align=(Align.CENTER, Align.CENTER, Align.MAX))
        hollow_limit = limit_builder.part

        # Shell and tray
        with BuildSketch(Plane.XY.offset(WALL_HEIGHT)):
            add(pcb_face)
            offset(amount=WALL_THICKNESS)
        extrude(dir=(0, 0, -1), until=Until.NEXT, target=floor_target)

        with BuildSketch(Plane.XY.offset(WALL_HEIGHT)):
            add(pcb_face)
        extrude(
            dir=(0, 0, -1), until=Until.NEXT, target=hollow_limit, mode=Mode.SUBTRACT
        )

        # Internal platform
        with BuildSketch(Plane.XY.offset(PLATFORM_Z)):
            add(pcb_face)
        extrude(amount=PLATFORM_THICKNESS)

        # Pillars
        with BuildSketch(Plane.XY.offset(PILLAR_BASE_HEIGHT)):
            add(hole_faces)
            offset(amount=PILLAR_BASE_OFFSET)
        extrude(amount=-(PILLAR_BASE_HEIGHT - (PLATFORM_Z + PLATFORM_THICKNESS)))

        with BuildSketch(Plane.XY.offset(PILLAR_TOP_HEIGHT)):
            add(hole_faces)
            offset(amount=PILLAR_TOP_OFFSET)
        extrude(amount=-(PILLAR_TOP_HEIGHT - PILLAR_BASE_HEIGHT))

        with BuildSketch(Plane.XY.offset(PILLAR_TOP_HEIGHT)):
            with Locations(hole_locs):
                Circle(radius=HOLE_RAD)
        extrude(amount=-HOLE_DEPTH, mode=Mode.SUBTRACT)

        # Wall cutout
        with Locations(CUTOUT_LOC):
            Box(CUTOUT_W, CUTOUT_D, CUTOUT_H, align=CUTOUT_ALIGN, mode=Mode.SUBTRACT)

        with BuildPart(mode=Mode.PRIVATE) as vis_builder:
            with Locations(CUTOUT_LOC):
                Box(CUTOUT_W, CUTOUT_D, CUTOUT_H, align=CUTOUT_ALIGN)
        cutout_vis = vis_builder.part
        cutout_vis.color = VIS_COLOR

    part = base.part
    if args.side == "right":
        part = mirror(part, Plane.YZ)

    with BuildPart() as final_case:
        add(part)

    if args.show:
        show(final_case.part, cutout_vis, names=["Case", "Cutout Guide"])

    export_stl(final_case.part, f"case/build/case_{args.side}.stl")


if __name__ == "__main__":
    main()
