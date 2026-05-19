import argparse
from build123d import *
from ocp_vscode import show

# Ergonomic Angles
TILT_ANGLE = 0
TENTING_ANGLE = 25

BASE_Z = -28
WALL_THICKNESS = 2
WALL_HEIGHT = 12.3
PLATFORM_THICKNESS = 2

# Pillars
PILLAR_BASE_HEIGHT = 2
PILLAR_BASE_OFFSET = 0
PILLAR_TOP_OFFSET = 0
PILLAR_TOP_HEIGHT = 3
HOLE_RAD = 0.8  # M2 Screws
PCB_CLEARANCE = 0.25

# Derived Constants
ABS_PILLAR_BASE_TOP_Z = PLATFORM_THICKNESS + PILLAR_BASE_HEIGHT
ABS_PILLAR_TOTAL_TOP_Z = ABS_PILLAR_BASE_TOP_Z + PILLAR_TOP_HEIGHT

# Battery Cutout
BATTERY_W = 60
BATTERY_H = 10
BATTERY_D = 70
BATTERY_Y_OFFSET = 42 + PCB_CLEARANCE
BATTERY_FILLET = 1

# Wiring Cutout
WIRING_W = 35
WIRING_H = 12
WIRING_D = 18

# Switch Cutout
SWITCH_CUTOUT_Y_OFFSET = 40 + PCB_CLEARANCE
SWITCH_CUTOUT_W = 10
SWITCH_CUTOUT_H = 6
SWITCH_CUTOUT_D = WALL_THICKNESS + 1
SWITCH_CUTOUT_FILLET = 1

# Charging Cutout
CHARGING_CUTOUT_X_OFFSET = 8.8 + PCB_CLEARANCE
CHARGING_CUTOUT_Y_OFFSET = 3.8
CHARGING_CUTOUT_Z_OFFSET = 6.35
CHARGING_CUTOUT_W = 12.0
CHARGING_CUTOUT_H = 6.0
CHARGING_CUTOUT_D = WALL_THICKNESS + 1
CHARGING_CUTOUT_FILLET = 1

FILLET_RAD = 1
CHAMFER_LEN = 1

VIS_COLOR = Color(1.0, 0.0, 0.0, alpha=0.3)


def main():
    parser = argparse.ArgumentParser(description="Generate case STL.")
    parser.add_argument("--side", nargs="?", default="left", choices=["left", "right"])
    parser.add_argument("--show", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--vis", action=argparse.BooleanOptionalAction, default=False)
    args = parser.parse_args()

    # Asset Imports
    pcb_wires = import_svg("case/build/pcb_outline.svg")
    hole_wires = import_svg("case/build/mounting_holes.svg")

    hole_wires.sort(key=lambda w: w.center().X)
    hole_wires = hole_wires[:6]

    with BuildSketch() as pcb_sketch:
        add(make_face(pcb_wires))
        offset(amount=PCB_CLEARANCE)
    pcb_face = pcb_sketch.sketch

    blocks = [make_face(w) for w in hole_wires]

    with BuildPart() as base:
        # Outer Shell
        with BuildPart(mode=Mode.PRIVATE) as outer_tray:
            with BuildSketch(Plane.XY.offset(PLATFORM_THICKNESS + WALL_HEIGHT)):
                add(pcb_face)
                offset(amount=WALL_THICKNESS)
            extrude(amount=-100)
            with Locations(
                Pos(pcb_face.bounding_box().center().X, 0, BASE_Z)
                * Rot(TILT_ANGLE, TENTING_ANGLE, 0)
            ):
                Box(
                    1000,
                    1000,
                    1000,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                    mode=Mode.INTERSECT,
                )
        add(outer_tray.part)

        # Wall Chamfer
        chamfer(base.faces().sort_by(Axis.Z)[-1].edges(), length=CHAMFER_LEN)

        # Inner Void Cutout
        with BuildPart(mode=Mode.PRIVATE) as inner_void:
            with BuildSketch(Plane.XY.offset(PLATFORM_THICKNESS + WALL_HEIGHT)):
                add(pcb_face)
            extrude(amount=-WALL_HEIGHT)
        add(inner_void.part, mode=Mode.SUBTRACT)

        # Internal Platform
        with BuildSketch(Plane.XY):
            add(pcb_face)
        extrude(amount=PLATFORM_THICKNESS)

        # Pillars
        with BuildSketch(Plane.XY.offset(ABS_PILLAR_BASE_TOP_Z)):
            add(blocks)
            offset(amount=PILLAR_TOP_OFFSET + PILLAR_BASE_OFFSET)
        extrude(amount=-PILLAR_BASE_HEIGHT)

        with BuildSketch(Plane.XY.offset(ABS_PILLAR_TOTAL_TOP_Z)):
            add(blocks)
        extrude(amount=-PILLAR_TOP_HEIGHT)

        with BuildSketch(Plane.XY.offset(ABS_PILLAR_TOTAL_TOP_Z)):
            with Locations([f.bounding_box().center() for f in blocks]):
                Circle(radius=HOLE_RAD)
        extrude(amount=-(PILLAR_TOP_HEIGHT + PILLAR_BASE_HEIGHT), mode=Mode.SUBTRACT)

        right_wall_x = base.part.bounding_box().max.X
        top_wall_y = base.part.bounding_box().max.Y

        # Battery Cutout
        with BuildPart(mode=Mode.PRIVATE) as battery_tool:
            with Locations(Pos(right_wall_x, top_wall_y - BATTERY_Y_OFFSET, 0)):
                Box(
                    BATTERY_D,
                    BATTERY_W,
                    BATTERY_H,
                    align=(Align.MAX, Align.CENTER, Align.MAX),
                )
                fillet(battery_tool.edges().filter_by(Axis.X), radius=BATTERY_FILLET)
        add(battery_tool.part, mode=Mode.SUBTRACT)

        # Wiring Cutout
        with BuildPart(mode=Mode.PRIVATE) as wiring_tool:
            with BuildSketch(Plane.XY.offset(PLATFORM_THICKNESS)):
                add(pcb_face)
            extrude(amount=-100)
            with Locations(
                Pos(right_wall_x - WALL_THICKNESS, top_wall_y, PLATFORM_THICKNESS)
            ):
                Box(
                    WIRING_D,
                    WIRING_W,
                    WIRING_H,
                    align=(Align.MAX, Align.MAX, Align.MAX),
                    mode=Mode.INTERSECT,
                )
        add(wiring_tool.part, mode=Mode.SUBTRACT)

        # Switch Cutout
        with BuildPart(mode=Mode.PRIVATE) as switch_cutout_tool:
            switch_y = top_wall_y - (
                SWITCH_CUTOUT_Y_OFFSET + WALL_THICKNESS + CHARGING_CUTOUT_Y_OFFSET
            )
            with Locations(Pos(right_wall_x, switch_y, PLATFORM_THICKNESS)):
                Box(
                    SWITCH_CUTOUT_D,
                    SWITCH_CUTOUT_W,
                    SWITCH_CUTOUT_H,
                    align=(Align.MAX, Align.CENTER, Align.MIN),
                )
                fillet(
                    switch_cutout_tool.edges().filter_by(Axis.X),
                    radius=SWITCH_CUTOUT_FILLET,
                )
        add(switch_cutout_tool.part, mode=Mode.SUBTRACT)

        # Charging Cutout
        with BuildPart(mode=Mode.PRIVATE) as charging_cutout_tool:
            charging_x = right_wall_x - (CHARGING_CUTOUT_X_OFFSET + WALL_THICKNESS)
            charging_z = PLATFORM_THICKNESS + CHARGING_CUTOUT_Z_OFFSET
            with Locations(
                Pos(charging_x, top_wall_y - CHARGING_CUTOUT_Y_OFFSET, charging_z)
            ):
                Box(
                    CHARGING_CUTOUT_W,
                    CHARGING_CUTOUT_D,
                    CHARGING_CUTOUT_H,
                    align=(Align.CENTER, Align.MAX, Align.CENTER),
                )
                fillet(
                    charging_cutout_tool.edges().filter_by(Axis.Y),
                    radius=CHARGING_CUTOUT_FILLET,
                )
        add(charging_cutout_tool.part, mode=Mode.SUBTRACT)

    # Visualizations
    visualisations_part = None
    if args.vis:
        with BuildPart() as vis_builder:
            add(battery_tool.part)
            add(wiring_tool.part)
            add(switch_cutout_tool.part)
            add(charging_cutout_tool.part)

        visualisations_part = vis_builder.part
        visualisations_part.color = VIS_COLOR

    part = base.part
    if args.side == "right":
        part = mirror(part, Plane.YZ)
        if visualisations_part is not None:
            visualisations_part = mirror(visualisations_part, Plane.YZ)
            visualisations_part.color = VIS_COLOR

    with BuildPart() as final_case:
        add(part)

    if args.show:
        show_parts = [final_case.part]
        show_names = ["Case"]

        if visualisations_part is not None:
            show_parts.append(visualisations_part)
            show_names.append("Visualizations")

        show(*show_parts, names=show_names)

    export_stl(final_case.part, f"case/build/case_{args.side}.stl")


if __name__ == "__main__":
    main()
