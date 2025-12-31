import argparse
from build123d import *
from ocp_vscode import show


def main():
    parser = argparse.ArgumentParser(description="Generate top plate STL.")
    parser.add_argument(
        "--side",
        nargs="?",
        default="left",
        choices=["left", "right"],
        help="Side (default: left)",
    )
    parser.add_argument(
        "--thickness", type=float, default=1.2, help="Thickness in mm (default: 1.2)"
    )
    parser.add_argument(
        "--extras",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Add extra features (default: False)",
    )
    parser.add_argument(
        "--show",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Show the model in the viewer (default: True)",
    )
    args = parser.parse_args()

    # Build top plate shape
    pcb_wires = import_svg("case/build/pcb_outline.svg")
    mounting_hole_wires = import_svg("case/build/mounting_holes.svg")
    switch_hole_wires = import_svg("case/build/switch_holes.svg")

    pcb_face = make_face(pcb_wires)
    mounting_hole_faces = [make_face(w) for w in mounting_hole_wires]
    switch_hole_faces = [make_face(w) for w in switch_hole_wires]

    with BuildPart() as base:
        add(pcb_face)
        extrude(amount=args.thickness)
        add(mounting_hole_faces)
        extrude(amount=args.thickness, mode=Mode.SUBTRACT)
        add(switch_hole_faces)
        extrude(amount=args.thickness, mode=Mode.SUBTRACT)

    part = base.part

    # Mirror based on side
    if args.side == "right":
        part = mirror(part, Plane.YZ)

    # Add extras such as logo and text
    with BuildPart() as final_case:
        add(part)

        if args.extras:
            extras_wires = import_svg(f"case/build/extras_{args.side}.svg")
            extras_wires = (
                extras_wires
                if args.side == "left"
                else [w.move(Location((-295.9, 0, 0))) for w in extras_wires]
            )
            add(extras_wires)
            extrude(amount=args.thickness + 1)

    if args.show:
        show(final_case)

    export_stl(final_case.part, f"case/build/top_plate_{args.side}.stl")


if __name__ == "__main__":
    main()
