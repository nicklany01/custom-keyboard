import argparse
from build123d import *
from ocp_vscode import show

BASE_THICKNESS = 2
PILLAR_HEIGHT = 4


def main():
    parser = argparse.ArgumentParser(description="Generate case STL.")
    parser.add_argument(
        "--side",
        nargs="?",
        default="left",
        choices=["left", "right"],
        help="Side (default: left)",
    )
    parser.add_argument(
        "--show",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Show the model in the viewer (default: True)",
    )
    args = parser.parse_args()

    pcb_wires = import_svg("case/build/pcb_outline.svg")
    mounting_hole_wires = import_svg("case/build/mounting_holes.svg")

    # Take only the left half of the mounting holes
    mounting_hole_wires.sort(key=lambda w: w.center().X)
    mounting_hole_wires = mounting_hole_wires[:6]

    pcb_face = make_face(pcb_wires)
    mounting_hole_faces = [make_face(w) for w in mounting_hole_wires][:6]

    with BuildPart() as base:
        with Locations((0, 0, -BASE_THICKNESS)):
            add(pcb_face)
            extrude(amount=BASE_THICKNESS)

            add(mounting_hole_faces)
            extrude(amount=BASE_THICKNESS + PILLAR_HEIGHT)

        with BuildSketch(Plane.XY) as mounting_holes:
            # Use bounding box centers of the original faces for accurate alignment
            locs = [f.bounding_box().center() for f in mounting_hole_faces]
            with Locations(locs):
                Circle(radius=0.8)
        extrude(amount=PILLAR_HEIGHT, mode=Mode.SUBTRACT)

    part = base.part

    # Mirror based on side
    if args.side == "right":
        part = mirror(part, Plane.YZ)

    with BuildPart() as final_case:
        add(part)

    if args.show:
        show(final_case)

    export_stl(final_case.part, f"case/build/case_{args.side}.stl")


if __name__ == "__main__":
    main()
