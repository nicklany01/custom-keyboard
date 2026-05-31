import argparse
import math
from build123d import *
from ocp_vscode import show

# Ergonomic Angles
TILT_ANGLE = 0
TENTING_ANGLE = 20

BASE_Z = -21
WALL_THICKNESS = 2
WALL_HEIGHT = 12.3
PLATFORM_THICKNESS = 2

# Raised Top Piece (screen bezel that sits above the wall)
TOP_PIECE_HEIGHT = 5.0

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
BATTERY_FILLET = 2

LOGO_SCALE = 0.8
LOGO_DEPTH = 1.0
TOP_OVERLAP = 2.0

# Front Text Configuration
TEXT_STR = "By Nick Lany"
TEXT_FONT_SIZE = 6
TEXT_FONT = "Arial"
TEXT_FONT_STYLE = FontStyle.BOLD
TEXT_LEFT_X = 40
TEXT_BOTTOM_Z = 1
TEXT_EXTRUDE_DEPTH = 16.5

# Wiring Cutout
WIRING_W = 35
WIRING_H = 12
WIRING_D = 18

# Switch Cutout
SWITCH_CUTOUT_Y_OFFSET = 45 + PCB_CLEARANCE
SWITCH_CUTOUT_W = 6
SWITCH_CUTOUT_H = 2
SWITCH_CUTOUT_D = WALL_THICKNESS + 1
SWITCH_CUTOUT_FILLET = 2

# Charging Cutout
CHARGING_CUTOUT_X_OFFSET = 8.8 + PCB_CLEARANCE
CHARGING_CUTOUT_Y_OFFSET = 3.8
CHARGING_CUTOUT_Z_OFFSET = 6.35
CHARGING_CUTOUT_W = 9.5
CHARGING_CUTOUT_H = 4
CHARGING_CUTOUT_D = WALL_THICKNESS + 1
CHARGING_CUTOUT_FILLET = 2

FILLET_RAD = 1
CHAMFER_LEN = 1

# Viewer Colors
VIS_COLOR = Color(1.0, 0.0, 0.0, alpha=0.3)
CASE_COLOR = Color(0.15, 0.15, 0.15)
INLAY_COLOR = Color(0.0, 0.3, 0.1)
TOP_COLOR = Color(0.5, 0.5, 0.5)


def main():
    parser = argparse.ArgumentParser(description="Generate case STL.")
    parser.add_argument("--side", nargs="?", default="left", choices=["left", "right"])
    parser.add_argument("--show", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--vis", action=argparse.BooleanOptionalAction, default=False)
    args = parser.parse_args()

    pcb_wires = import_svg("case/build/pcb_outline.svg")
    hole_wires = import_svg("case/build/mounting_holes.svg")
    logo_wires = import_svg("assets/logo.svg")
    top_edge_wires = Wire.combine(import_svg("case/build/top_edge.svg"))
    top_cutout_wires = Wire.combine(import_svg("case/build/top_cutout.svg"))

    inlay_pieces = []
    visualizations_part = None

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

        # Unified Bounding Box Context for All Cutouts
        case_bbox = base.part.bounding_box()

        # Battery Cutout
        with BuildPart(mode=Mode.PRIVATE) as battery_tool:
            with Locations(Pos(case_bbox.max.X, case_bbox.max.Y - BATTERY_Y_OFFSET, 0)):
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
                Pos(
                    case_bbox.max.X - WALL_THICKNESS,
                    case_bbox.max.Y,
                    PLATFORM_THICKNESS,
                )
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
            switch_y = case_bbox.max.Y - (
                SWITCH_CUTOUT_Y_OFFSET + WALL_THICKNESS + CHARGING_CUTOUT_Y_OFFSET
            )
            with Locations(Pos(case_bbox.max.X, switch_y, PLATFORM_THICKNESS)):
                Box(
                    SWITCH_CUTOUT_D,
                    SWITCH_CUTOUT_W,
                    WALL_HEIGHT,
                    align=(Align.MAX, Align.CENTER, Align.MIN),
                )
                fillet(
                    switch_cutout_tool.edges().filter_by(Axis.X).sort_by(Axis.Z)[:2],
                    radius=SWITCH_CUTOUT_FILLET,
                )
        add(switch_cutout_tool.part, mode=Mode.SUBTRACT)

        # Charging Cutout
        with BuildPart(mode=Mode.PRIVATE) as charging_cutout_tool:
            charging_x = case_bbox.max.X - (CHARGING_CUTOUT_X_OFFSET + WALL_THICKNESS)
            charging_z = PLATFORM_THICKNESS + CHARGING_CUTOUT_Z_OFFSET
            charging_hole_bottom = charging_z - CHARGING_CUTOUT_H / 2
            charging_cutout_height = (
                PLATFORM_THICKNESS + WALL_HEIGHT
            ) - charging_hole_bottom
            with Locations(
                Pos(
                    charging_x,
                    case_bbox.max.Y - CHARGING_CUTOUT_Y_OFFSET,
                    charging_hole_bottom,
                )
            ):
                Box(
                    CHARGING_CUTOUT_W,
                    CHARGING_CUTOUT_D,
                    charging_cutout_height,
                    align=(Align.CENTER, Align.MAX, Align.MIN),
                )
                fillet(
                    charging_cutout_tool.edges().filter_by(Axis.Y).sort_by(Axis.Z)[:2],
                    radius=CHARGING_CUTOUT_FILLET,
                )
        add(charging_cutout_tool.part, mode=Mode.SUBTRACT)

        # Logo Cutout
        with BuildSketch(mode=Mode.PRIVATE) as logo_sketch:
            for w in logo_wires:
                try:
                    add(make_face(w))
                except Exception:
                    pass

        if logo_sketch.sketch:
            pcb_bbox = pcb_face.bounding_box()
            pcb_center = pcb_bbox.center()
            target_width = pcb_bbox.size.X / math.cos(math.radians(TENTING_ANGLE))
            target_height = pcb_bbox.size.Y

            logo_bbox = logo_sketch.sketch.bounding_box()
            initial_logo_width = logo_bbox.size.X
            initial_logo_height = logo_bbox.size.Y

            if initial_logo_width > 0 and initial_logo_height > 0:
                logo = logo_sketch.sketch.translate(
                    (-logo_bbox.center().X, -logo_bbox.center().Y, 0)
                )
                scale_factor = (
                    min(
                        target_width / initial_logo_width,
                        target_height / initial_logo_height,
                    )
                    * LOGO_SCALE
                )
                logo = logo.scale(scale_factor)

                # Pre-mirror for left side, and skip for right side (globally mirrored later)
                if args.side == "left":
                    logo = mirror(logo, Plane.YZ)

                bottom_plane = (
                    Plane.XY
                    * Pos(pcb_center.X, 0, BASE_Z)
                    * Rot(TILT_ANGLE, TENTING_ANGLE, 0)
                )

                with BuildPart(mode=Mode.PRIVATE) as logo_builder:
                    with BuildSketch(bottom_plane):
                        with Locations(Pos(0, pcb_center.Y)):
                            add(logo)
                    extrude(amount=LOGO_DEPTH)

                add(logo_builder.part, mode=Mode.SUBTRACT)
                inlay_pieces.append(logo_builder.part)

        # Front Wall Text Cutout & Inlay
        front_plane = Plane(
            origin=(case_bbox.center().X, case_bbox.min.Y, BASE_Z),
            x_dir=(1, 0, 0),
            z_dir=(0, -1, 0),
        )
        text_left_x = (case_bbox.min.X - case_bbox.center().X) / math.cos(
            math.radians(TENTING_ANGLE)
        ) + TEXT_LEFT_X

        with BuildPart(mode=Mode.PRIVATE) as text_tool:
            with BuildSketch(front_plane) as text_sketch:
                with Locations(
                    Rot(0, 0, -TENTING_ANGLE) * Pos(text_left_x, TEXT_BOTTOM_Z)
                ):
                    Text(
                        TEXT_STR,
                        font_size=TEXT_FONT_SIZE,
                        font=TEXT_FONT,
                        font_style=TEXT_FONT_STYLE,
                        align=(Align.MIN, Align.MIN),
                    )

            if args.side == "right":
                extrude(
                    mirror(
                        text_sketch.sketch,
                        Plane(
                            origin=text_sketch.sketch.bounding_box().center(),
                            x_dir=(0, -1, 0),
                            z_dir=Vector(
                                math.cos(math.radians(-TENTING_ANGLE)),
                                0,
                                math.sin(math.radians(-TENTING_ANGLE)),
                            ),
                        ),
                    ),
                    amount=-TEXT_EXTRUDE_DEPTH,
                )
            else:
                extrude(text_sketch.sketch, amount=-TEXT_EXTRUDE_DEPTH)

        with BuildPart(mode=Mode.PRIVATE) as text_inlay:
            add(base.part)
            add(text_tool.part, mode=Mode.INTERSECT)

        add(text_tool.part, mode=Mode.SUBTRACT)
        if text_inlay.part:
            inlay_pieces.append(text_inlay.part)

        inlay_part = Compound(inlay_pieces) if inlay_pieces else None

    # Raised Top Piece
    top_part = None
    top_edge_faces = [make_face(w) for w in top_edge_wires]
    top_cutout_faces = [make_face(w) for w in top_cutout_wires]
    if top_edge_faces:
        top_piece_z = PLATFORM_THICKNESS + WALL_HEIGHT
        with BuildPart() as top_builder:
            with BuildSketch(Plane.XY.offset(top_piece_z - TOP_OVERLAP)):
                add(pcb_face)
                offset(amount=WALL_THICKNESS)
                add(top_edge_faces, mode=Mode.INTERSECT)
            extrude(amount=TOP_PIECE_HEIGHT + TOP_OVERLAP)

            # Screen windows (subtracted through the entire height)
            if top_cutout_faces:
                with BuildSketch(Plane.XY.offset(top_piece_z - TOP_OVERLAP)):
                    add(top_cutout_faces)
                extrude(amount=TOP_PIECE_HEIGHT + TOP_OVERLAP, mode=Mode.SUBTRACT)

            # Hollow out starting 2mm lower
            with BuildSketch(Plane.XY.offset(top_piece_z - TOP_OVERLAP)):
                add(pcb_face)
                offset(amount=WALL_THICKNESS)
                add(top_edge_faces, mode=Mode.INTERSECT)
                offset(amount=-WALL_THICKNESS)
            extrude(
                amount=TOP_PIECE_HEIGHT - PLATFORM_THICKNESS + TOP_OVERLAP,
                mode=Mode.SUBTRACT,
            )

            # Switch projection
            with BuildPart(mode=Mode.PRIVATE) as switch_proj:
                with BuildSketch(Plane.XY.offset(PLATFORM_THICKNESS + SWITCH_CUTOUT_H)):
                    add(pcb_face)
                    offset(amount=WALL_THICKNESS)
                    add(pcb_face, mode=Mode.SUBTRACT)
                extrude(amount=WALL_HEIGHT - SWITCH_CUTOUT_H)

                with Locations(
                    Pos(case_bbox.max.X, switch_y, PLATFORM_THICKNESS + SWITCH_CUTOUT_H)
                ):
                    Box(
                        SWITCH_CUTOUT_D,
                        SWITCH_CUTOUT_W,
                        WALL_HEIGHT - SWITCH_CUTOUT_H + 1,
                        align=(Align.MAX, Align.CENTER, Align.MIN),
                        mode=Mode.INTERSECT,
                    )
            if switch_proj.part:
                add(switch_proj.part)

            # Charging projection
            charging_hole_top = charging_z + CHARGING_CUTOUT_H / 2
            charging_proj_height = (
                PLATFORM_THICKNESS + WALL_HEIGHT
            ) - charging_hole_top
            with BuildPart(mode=Mode.PRIVATE) as charging_proj:
                with BuildSketch(Plane.XY.offset(charging_hole_top)):
                    add(pcb_face)
                    offset(amount=WALL_THICKNESS)
                    add(pcb_face, mode=Mode.SUBTRACT)
                extrude(amount=charging_proj_height)

                with Locations(
                    Pos(
                        charging_x,
                        case_bbox.max.Y - CHARGING_CUTOUT_Y_OFFSET,
                        charging_hole_top,
                    )
                ):
                    Box(
                        CHARGING_CUTOUT_W,
                        CHARGING_CUTOUT_D,
                        charging_proj_height + 1,
                        align=(Align.CENTER, Align.MAX, Align.MIN),
                        mode=Mode.INTERSECT,
                    )
            if charging_proj.part:
                add(charging_proj.part)
        # Interlock fit: subtract bottom case to form matching chamfer lips
        top_part = top_builder.part - base.part

    # Visualizations
    if args.vis:
        with BuildPart() as vis_builder:
            add(battery_tool.part)
            add(wiring_tool.part)
            add(switch_cutout_tool.part)
            add(charging_cutout_tool.part)
        visualizations_part = vis_builder.part

    # Side Mirroring
    part = base.part
    if args.side == "right":
        part = mirror(part, Plane.YZ)
        if inlay_part is not None:
            inlay_part = mirror(inlay_part, Plane.YZ)
        if top_part is not None:
            top_part = mirror(top_part, Plane.YZ)
        if visualizations_part is not None:
            visualizations_part = mirror(visualizations_part, Plane.YZ)

    with BuildPart() as final_case:
        add(part)

    if args.show:
        final_case.part.color = CASE_COLOR
        show_parts = [final_case.part]
        show_names = ["Case"]

        if inlay_part is not None:
            inlay_part.color = INLAY_COLOR
            show_parts.append(inlay_part)
            show_names.append("Inlay Features")

        if top_part is not None:
            top_part.color = TOP_COLOR
            show_parts.append(top_part)
            show_names.append("Top Piece")

        if visualizations_part is not None:
            visualizations_part.color = VIS_COLOR
            show_parts.append(visualizations_part)
            show_names.append("Visualizations")

        show(*show_parts, names=show_names)

    # Multi-Material Export
    output_solids = [final_case.part]
    if inlay_part is not None:
        output_solids.append(inlay_part)
    if top_part is not None:
        output_solids.append(top_part)
    export_step(Compound(output_solids), f"case/build/case_{args.side}.step")

    export_stl(final_case.part, f"case/build/case_{args.side}_main.stl")
    if inlay_part is not None:
        export_stl(inlay_part, f"case/build/case_{args.side}_inlay.stl")
    if top_part is not None:
        export_stl(top_part, f"case/build/case_{args.side}_top.stl")


if __name__ == "__main__":
    main()
