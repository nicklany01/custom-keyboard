import argparse
from build123d import *
from ocp_vscode import show

# Ergonomic Angles
TILT_ANGLE = 0
TENTING_ANGLE = 25
BASE_Z = -32
FLOOR_THICKNESS = 2

WALL_THICKNESS = 2
WALL_HEIGHT = 12

PLATFORM_Z = -4
PLATFORM_THICKNESS = 2

PILLAR_BASE_HEIGHT = 2
PILLAR_BASE_OFFSET = 0
PILLAR_TOP_OFFSET = 0
PILLAR_TOP_HEIGHT = 3
HOLE_RAD = 0.8

# Derived Constants
ABS_PILLAR_BASE_TOP_Z = PLATFORM_Z + PLATFORM_THICKNESS + PILLAR_BASE_HEIGHT
ABS_PILLAR_TOTAL_TOP_Z = ABS_PILLAR_BASE_TOP_Z + PILLAR_TOP_HEIGHT

CUTOUT_W = 60
CUTOUT_H = 10
CUTOUT_D = 10
CUTOUT_LOC = Pos(140, 108, PLATFORM_Z) * Rot(0, 0, 90)
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
        cx = pcb_face.bounding_box().center().X
        tilt_loc = Pos(cx, 0, BASE_Z) * Rot(TILT_ANGLE, TENTING_ANGLE, 0)

        # Outer Shell
        with BuildPart(mode=Mode.PRIVATE) as outer_tray:
            with BuildSketch(
                Plane.XY.offset(PLATFORM_Z + PLATFORM_THICKNESS + WALL_HEIGHT)
            ):
                add(pcb_face)
                offset(amount=WALL_THICKNESS)
            extrude(amount=-100)
            with Locations(tilt_loc):
                Box(
                    1000,
                    1000,
                    1000,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                    mode=Mode.INTERSECT,
                )
        add(outer_tray.part)

        # Inner Void Cutout
        with BuildPart(mode=Mode.PRIVATE) as inner_void:
            with BuildSketch(
                Plane.XY.offset(PLATFORM_Z + PLATFORM_THICKNESS + WALL_HEIGHT)
            ):
                add(pcb_face)
            extrude(amount=-100)
            with Locations(tilt_loc * Pos(0, 0, FLOOR_THICKNESS)):
                Box(
                    1000,
                    1000,
                    1000,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                    mode=Mode.INTERSECT,
                )
        add(inner_void.part, mode=Mode.SUBTRACT)

        # Internal platform
        with BuildSketch(Plane.XY.offset(PLATFORM_Z)):
            add(pcb_face)
        extrude(amount=PLATFORM_THICKNESS)

        # Battery resting platform
        with BuildPart(mode=Mode.PRIVATE) as lower_platform:
            with Locations(CUTOUT_LOC * Pos(0, 0, -CUTOUT_H)):
                Box(
                    CUTOUT_W,
                    1000,
                    PLATFORM_THICKNESS,
                    align=(Align.MIN, Align.CENTER, Align.MAX),
                )
            add(inner_void.part, mode=Mode.INTERSECT)
        add(lower_platform.part)

        # Pillars
        with BuildSketch(Plane.XY.offset(ABS_PILLAR_BASE_TOP_Z)):
            add(hole_faces)
            offset(amount=PILLAR_TOP_OFFSET + PILLAR_BASE_OFFSET)
        extrude(amount=-PILLAR_BASE_HEIGHT)

        with BuildSketch(Plane.XY.offset(ABS_PILLAR_TOTAL_TOP_Z)):
            add(hole_faces)
        extrude(amount=-PILLAR_TOP_HEIGHT)

        with BuildSketch(Plane.XY.offset(ABS_PILLAR_TOTAL_TOP_Z)):
            with Locations(hole_locs):
                Circle(radius=HOLE_RAD)
        extrude(amount=-(PILLAR_TOP_HEIGHT + PILLAR_BASE_HEIGHT), mode=Mode.SUBTRACT)

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
