"""Build a Staunton-style chess pawn as a solid of revolution.

A pawn is a turned piece, so the whole thing is one closed profile revolved 360
degrees about the Z axis — base, cove, collar bead, body, neck and head ball.
The head is part of that profile rather than a separate sphere unioned on top: a
circle centred on the axis generates an exact sphere when revolved, and keeping
it in the profile avoids the ledge a union would leave where the ball's lower
half bulges wider than the neck.

Units are millimetres, Z is up, the base sits on the Z=0 plane.
"""

import math

import cadquery as cq

# Overall proportions. A Staunton pawn is a little over twice as tall as its
# base is wide; the tests assert that ratio holds.
BASE_RADIUS = 5.6
HEAD_RADIUS = 3.2
HEAD_CENTRE_Z = 20.3

# The head is the top of the profile, so the height falls out of the geometry
# instead of being a number that has to be kept in step with it.
TOTAL_HEIGHT = HEAD_CENTRE_Z + HEAD_RADIUS

# Where the neck hands over to the head ball, as a height. The join radius is
# derived from the head circle so the two curves meet exactly rather than at a
# pair of numbers that can drift apart. Joining below the equator leaves the
# small shoulder under the ball that a turned pawn actually has.
JOIN_Z = 17.80
JOIN_R = (HEAD_RADIUS**2 - (JOIN_Z - HEAD_CENTRE_Z) ** 2) ** 0.5
NECK_TOP = (JOIN_R, JOIN_Z)

# Profile of the revolved body, as (radius, height) pairs in the XZ workplane.
#
# Two behaviours of cq.Workplane.spline() that cost some trial and error:
#   * it starts at its *first* listed point, not at the current pen position,
#     so every segment below begins on the previous segment's last point (via
#     [previous[-1]]) or the wire comes out disconnected and close() raises
#     StdFail_NotDone;
#   * the listed points are interpolated through, so they are points the curve
#     really passes, not control points.
RIM_END = (BASE_RADIUS - 0.50, 1.20)
COVE_POINTS = [RIM_END, (4.95, 1.55), (4.20, 2.00), (3.45, 2.35)]
BEAD_POINTS = [COVE_POINTS[-1], (3.95, 2.62), (4.10, 2.95), (3.85, 3.25)]
BODY_POINTS = [BEAD_POINTS[-1], (3.10, 5.40), (2.40, 8.60), (2.00, 12.40)]
# Waist at about r=1.8, then a flare up to the join. Nothing here may rise above
# JOIN_Z — check_profile() enforces that.
NECK_POINTS = [BODY_POINTS[-1], (1.80, 14.60), (1.82, 16.40), (2.20, 17.35), NECK_TOP]

# Arc over the head. The middle point sits at the latitude halfway between the
# join and the pole, so it is genuinely mid-arc and threePointArc cannot resolve
# to the complementary arc. The result is a circular arc, so revolving it gives
# an exact sphere.
_join_angle = math.atan2(JOIN_Z - HEAD_CENTRE_Z, JOIN_R)
_mid_angle = (_join_angle + math.pi / 2) / 2
HEAD_ARC_POINT = (
    HEAD_RADIUS * math.cos(_mid_angle),
    HEAD_CENTRE_Z + HEAD_RADIUS * math.sin(_mid_angle),
)
HEAD_POLE = (0.0, TOTAL_HEIGHT)


def build_profile() -> "cq.Workplane[str]":
    """Return the closed half-section of the pawn, ready to revolve."""
    return (
        cq.Workplane("XZ")
        .moveTo(0.0, 0.0)
        # Flat bottom out to the rim.
        .lineTo(BASE_RADIUS, 0.0)
        # Rounded bottom edge: the rim is the only sharp edge on the piece.
        .threePointArc((BASE_RADIUS - 0.05, 0.62), RIM_END)
        .spline(COVE_POINTS)  # concave cove above the base
        .spline(BEAD_POINTS)  # collar bead
        .spline(BODY_POINTS)  # long concave taper
        .spline(NECK_POINTS)  # neck, flaring to meet the head
        .threePointArc(HEAD_ARC_POINT, HEAD_POLE)  # head ball
        .lineTo(0.0, 0.0)  # back down the axis to the start
        .close()
    )


def check_profile() -> None:
    """Fail loudly on a profile that would build a broken or ugly solid.

    Catches bad edits here rather than as a lumpy mesh further down the line.
    """
    edges = build_profile().ctx.pendingWires[0].Edges()
    head_arc = max(edges, key=lambda e: e.Center().z)

    # The silhouette edges (not the axis line, not the head arc) may only rise
    # as far as the join. An edge poking higher means the neck spline overshoots
    # and would cut back through the ball.
    # XZ workplane: x is radius, z is height.
    for edge in edges:
        if edge is head_arc:
            continue
        points = edge.sample(64)[0]
        if max(p.x for p in points) < 1e-6:
            continue  # the segment lying on the axis
        top = max(p.z for p in points)
        if top > JOIN_Z + 1e-6:
            msg = f"profile rises to z={top:.2f} above the neck/head join at z={JOIN_Z:.2f}"
            raise ValueError(msg)

    # The arc over the head really is the head circle, i.e. the revolution is a
    # true sphere and not a blob that happens to start and end in the right
    # places.
    for p in head_arc.sample(32)[0]:
        radius_here = (p.x**2 + (p.z - HEAD_CENTRE_Z) ** 2) ** 0.5
        if abs(radius_here - HEAD_RADIUS) > 0.02:
            msg = f"head arc leaves the head circle at z={p.z:.2f} (radius {radius_here:.3f})"
            raise ValueError(msg)

    # Shape sanity: a pawn whose body does not narrow below the collar, or whose
    # neck does not pinch, is a bucket.
    if BODY_POINTS[-1][0] >= BEAD_POINTS[2][0]:
        msg = "body must taper narrower than the collar bead"
        raise ValueError(msg)
    waist = min(pt[0] for pt in NECK_POINTS)
    if waist >= BODY_POINTS[-1][0]:
        msg = "neck must narrow below the body before flaring into the head"
        raise ValueError(msg)


def build_pawn() -> "cq.Workplane[cq.Solid]":
    """Return the pawn as a single revolved solid."""
    check_profile()
    return build_profile().revolve(360, (0, 0), (0, 1)).clean()


def main() -> None:
    """Print a short summary of the model, for a quick eyeball check."""
    pawn = build_pawn()
    solid = pawn.val()
    bbox = solid.BoundingBox()
    print(f"valid solid:   {solid.isValid()}")
    print(f"volume:        {solid.Volume():.2f} mm^3")
    print(f"surface area:  {solid.Area():.2f} mm^2")
    print(f"solid faces:   {len(solid.Faces())}")
    print(f"bounding box:  {bbox.xlen:.2f} x {bbox.ylen:.2f} x {bbox.zlen:.2f} mm")
    print(f"z range:       {bbox.zmin:.2f} .. {bbox.zmax:.2f} mm")
    print(f"height/base:   {bbox.zlen / (2 * BASE_RADIUS):.2f} (want ~2.0)")
    print(f"target height: {TOTAL_HEIGHT:.2f} mm")


if __name__ == "__main__":
    main()
