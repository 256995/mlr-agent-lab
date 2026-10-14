"""Tests for the pawn model and its mesh export."""

import math

import pytest

import export_pawn_mesh as ex
from pawn_model import (
    BASE_RADIUS,
    BEAD_POINTS,
    BODY_POINTS,
    HEAD_CENTRE_Z,
    HEAD_RADIUS,
    JOIN_Z,
    NECK_POINTS,
    TOTAL_HEIGHT,
    build_pawn,
    build_profile,
    check_profile,
)


@pytest.fixture(scope="module")
def pawn():
    return build_pawn().val()


def test_solid_is_valid(pawn):
    assert pawn.isValid()


def test_solid_is_one_piece(pawn):
    assert len(pawn.Solids()) == 1


def test_dimensions_match_the_spec(pawn):
    box = pawn.BoundingBox()
    assert box.zlen == pytest.approx(TOTAL_HEIGHT, abs=0.02)
    assert box.xlen == pytest.approx(2 * BASE_RADIUS, abs=0.1)
    assert box.ylen == pytest.approx(2 * BASE_RADIUS, abs=0.1)


def test_sits_on_the_floor(pawn):
    """The piece stands up in the viewer only if the base is flat at z=0."""
    assert pawn.BoundingBox().zmin == pytest.approx(0.0, abs=0.02)


def test_is_taller_than_it_is_wide(pawn):
    """A Staunton pawn reads as roughly 2:1; a squat one looks like a stopper."""
    box = pawn.BoundingBox()
    ratio = box.zlen / (2 * BASE_RADIUS)
    assert 1.8 < ratio < 2.4


def test_profile_is_a_single_closed_wire():
    wires = build_profile().ctx.pendingWires
    assert len(wires) == 1
    # Bottom, rim arc, 4 body splines, head arc, axis line.
    assert len(wires[0].Edges()) == 8


def test_nothing_shrinks_inside_the_head():
    """The neck stops at the join, so the head ball is never cut into."""
    check_profile()
    assert max(pt[1] for pt in NECK_POINTS) == pytest.approx(JOIN_Z)
    assert JOIN_Z < HEAD_CENTRE_Z


def test_neck_pinches_below_the_body():
    waist = min(pt[0] for pt in NECK_POINTS)
    assert waist < BODY_POINTS[-1][0]
    assert BODY_POINTS[-1][0] < BEAD_POINTS[2][0]


def test_head_is_a_real_sphere(pawn):
    """Volume of the piece must be within a percent of a sphere-capped estimate.

    A loose check, but it fails if the head arc degrades into a cone or the
    revolve angle is wrong.
    """
    hemisphere = (2 / 3) * math.pi * HEAD_RADIUS**3
    assert pawn.Volume() > hemisphere * 1.5


def test_mesh_export_is_closed_and_wound(pawn):
    points, triangles = pawn.tessellate(ex.DEFLECTION, ex.ANGULAR_DEFLECTION)
    verts, tris = ex.weld(points, triangles)
    # Welding must actually have merged the duplicates the tessellator leaves
    # on shared face boundaries, or the exported mesh is needlessly heavy.
    assert len(verts) < len(points)

    uses: dict[frozenset, int] = {}
    for i, j, k in tris:
        for edge in ((i, j), (j, k), (k, i)):
            key = frozenset(edge)
            uses[key] = uses.get(key, 0) + 1

    assert all(count == 2 for count in uses.values()), "mesh is not a closed manifold"


def test_mesh_volume_follows_the_solid(pawn):
    payload = ex.build_mesh()
    pos, idx = payload["position"], payload["index"]
    volume = 0.0
    for t in range(0, len(idx), 3):
        a, b, c = (pos[3 * idx[t + n] : 3 * idx[t + n] + 3] for n in range(3))
        volume += (
            a[0] * (b[1] * c[2] - c[1] * b[2])
            - a[1] * (b[0] * c[2] - c[0] * b[2])
            + a[2] * (b[0] * c[1] - c[0] * b[1])
        ) / 6
    # Tessellation is an inside approximation, so it comes in slightly under.
    assert 0.98 < volume / pawn.Volume() <= 1.0


def test_mesh_normals_are_unit_length():
    payload = ex.build_mesh()
    normals = payload["normal"]
    for i in range(0, len(normals), 3):
        length = math.sqrt(normals[i] ** 2 + normals[i + 1] ** 2 + normals[i + 2] ** 2)
        assert length == pytest.approx(1.0, abs=1e-3)


def test_mesh_indices_stay_in_range():
    payload = ex.build_mesh()
    count = len(payload["position"]) // 3
    assert payload["index"]
    assert max(payload["index"]) < count
    assert min(payload["index"]) >= 0


def test_creases_survive_the_normal_bake():
    """The base rim must keep a hard edge instead of shading into the flank.

    The bottom face meets the flank at about 90 degrees, which is over the
    crease angle, so the vertices on that boundary get split into two entries
    with different normals. A fully smooth bake would average them into one
    diagonal normal and the pawn would look like it has no base at all.
    """
    solid = build_pawn().val()
    welded, tris = ex.weld(*solid.tessellate(ex.DEFLECTION, ex.ANGULAR_DEFLECTION))
    face_n = ex.face_normals(welded, tris)
    groups = ex.smooth_groups(tris, face_n)
    out_pos, out_norm, _ = ex.vertex_normals(welded, tris, face_n, groups)

    # One output vertex per (position, smooth group), so a crease shows up as
    # the same position appearing twice with two different normals.
    by_position: dict[tuple[float, float, float], list[tuple[float, float, float]]] = {}
    for pos, nrm in zip(out_pos, out_norm, strict=True):
        by_position.setdefault(tuple(round(c, 5) for c in pos), []).append(nrm)

    # Only the rim matters: the flat bottom meets the flank there.
    rim = [n for p, n in by_position.items() if p[2] < 0.02 and len(n) > 1]
    assert rim, "no base vertex was split, so the rim shades smooth and vanishes"

    angles = []
    for norms in rim:
        a, b = norms[0], norms[1]
        dot = sum(x * y for x, y in zip(a, b, strict=True))
        angles.append(math.degrees(math.acos(max(-1.0, min(1.0, dot)))))

    # The rim is very close to a right angle, so the two normals must sit far
    # apart. A smooth bake would give 0 degrees everywhere.
    assert min(angles) > 45, f"smallest rim split is only {min(angles):.1f} deg"
