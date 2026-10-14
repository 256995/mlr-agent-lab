"""Tessellate the pawn and write it out as JSON for the browser viewer.

CadQuery will tessellate a solid into points and triangles, but it gives no
normals, and its STL export would throw away the difference between the smooth
flanks and the one sharp edge at the base rim. So this welds the coincident
vertices that the tessellator duplicates along shared faces, splits them again
where the surfaces meet at a crease, and writes smooth normals per group — which
is what makes the flanks read as curved and the rim read as a real edge.

Coordinates stay in the CAD convention (millimetres, Z up, base on Z=0); the
viewer rotates them into its own up axis.
"""

import json
import math
from collections import defaultdict
from pathlib import Path

from pawn_model import BASE_RADIUS, HEAD_RADIUS, TOTAL_HEIGHT, build_pawn

OUT_PATH = Path(__file__).resolve().parent / "docs" / "pawn.json"

# Tessellation tolerances, in millimetres and radians. Smaller is rounder and
# bigger; these hold the surface to 20 microns and keep the file well under a
# megabyte.
DEFLECTION = 0.02
ANGULAR_DEFLECTION = 0.2

# Dihedral angle above which a shared edge counts as a crease and stops sharing
# a normal between the two faces. 30 degrees keeps the flank shading smooth
# while leaving the base rim and the neck/head shoulder crisp.
CREASE_ANGLE = math.radians(30.0)
CREASE_COS = math.cos(CREASE_ANGLE)


def weld(
    points: list, triangles: list[tuple[int, int, int]]
) -> tuple[list[tuple[float, float, float]], list[tuple[int, int, int]]]:
    """Merge the duplicated vertices the tessellator leaves on shared edges."""
    verts: list[tuple[float, float, float]] = []
    seen: dict[tuple[float, float, float], int] = {}
    tris: list[tuple[int, int, int]] = []

    for tri in triangles:
        welded = []
        for idx in tri:
            p = points[idx]
            # Snapping to 1e-6 mm merges duplicates from neighbouring faces
            # without collapsing anything real — the finest feature here is a
            # 0.05 mm fillet.
            key = (round(p.x, 6), round(p.y, 6), round(p.z, 6))
            if key not in seen:
                seen[key] = len(verts)
                verts.append(key)
            welded.append(seen[key])
        i, j, k = welded
        if i != j and j != k and i != k:
            tris.append((i, j, k))

    return verts, tris


def face_normals(
    verts: list[tuple[float, float, float]], tris: list[tuple[int, int, int]]
) -> list[tuple[float, float, float]]:
    """Unnormalized normals; the length is twice the triangle area."""
    out = []
    for i, j, k in tris:
        ax, ay, az = verts[j][0] - verts[i][0], verts[j][1] - verts[i][1], verts[j][2] - verts[i][2]
        bx, by, bz = verts[k][0] - verts[i][0], verts[k][1] - verts[i][1], verts[k][2] - verts[i][2]
        out.append((ay * bz - az * by, az * bx - ax * bz, ax * by - ay * bx))
    return out


def smooth_groups(
    tris: list[tuple[int, int, int]], normals: list[tuple[float, float, float]]
) -> list[int]:
    """Group triangles that meet smoothly, so each group gets one normal set.

    Triangles sharing an edge are merged when the angle between their normals is
    under the crease angle; anything sharper stays split, which is what keeps a
    hard edge looking hard.
    """
    parent = list(range(len(tris)))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    by_edge: dict[frozenset[int], list[int]] = defaultdict(list)
    for ti, tri in enumerate(tris):
        for edge in ((tri[0], tri[1]), (tri[1], tri[2]), (tri[2], tri[0])):
            by_edge[frozenset(edge)].append(ti)

    for shared in by_edge.values():
        for a in range(len(shared)):
            for b in range(a + 1, len(shared)):
                na, nb = normals[shared[a]], normals[shared[b]]
                la = math.sqrt(sum(c * c for c in na))
                lb = math.sqrt(sum(c * c for c in nb))
                if la == 0.0 or lb == 0.0:
                    continue
                if (na[0] * nb[0] + na[1] * nb[1] + na[2] * nb[2]) / (la * lb) >= CREASE_COS:
                    union(shared[a], shared[b])

    return [find(ti) for ti in range(len(tris))]


def vertex_normals(
    verts: list[tuple[float, float, float]],
    tris: list[tuple[int, int, int]],
    normals: list[tuple[float, float, float]],
    group: list[int],
) -> tuple[list[tuple[float, float, float]], list[tuple[float, float, float]], list[tuple[int, int, int]]]:
    """Split welded vertices at creases and give each part an area-weighted normal.

    Returns the new position list, matching normals, and a remap from
    (old vertex, smooth group) to the new index, so the index buffer can be
    rewritten against them.
    """
    incident: dict[int, dict[int, list[int]]] = defaultdict(dict)
    for ti, tri in enumerate(tris):
        for vi in tri:
            incident[vi].setdefault(group[ti], []).append(ti)

    out_verts: list[tuple[float, float, float]] = []
    out_normals: list[tuple[float, float, float]] = []
    remap: dict[tuple[int, int], int] = {}

    for vi, groups in incident.items():
        for gi, tris_here in groups.items():
            # Summing the unnormalized face normals weights each by its area, so
            # a sliver contributes proportionally less than a broad facet.
            acc = [0.0, 0.0, 0.0]
            for ti in tris_here:
                for axis in range(3):
                    acc[axis] += normals[ti][axis]
            length = math.sqrt(sum(c * c for c in acc))
            if length == 0.0:
                acc = list(normals[tris_here[0]])
                length = math.sqrt(sum(c * c for c in acc)) or 1.0
            remap[(vi, gi)] = len(out_verts)
            out_verts.append(verts[vi])
            out_normals.append(tuple(c / length for c in acc))

    missing = [
        (ti, vi, group[ti])
        for ti, tri in enumerate(tris)
        for vi in tri
        if (vi, group[ti]) not in remap
    ]
    if missing:
        ti, vi, gi = missing[0]
        msg = (
            f"{len(missing)} unmapped (vertex, group) pairs; first: triangle {ti} "
            f"{tris[ti]} group {gi} vertex {vi} groups={sorted(incident[vi])}"
        )
        raise RuntimeError(msg)

    new_tris = [tuple(remap[(vi, group[ti])] for vi in tri) for ti, tri in enumerate(tris)]
    return out_verts, out_normals, new_tris


def build_mesh(solid_tolerance: float = DEFLECTION) -> dict:
    """Tessellate the pawn and return the buffer payload as a plain dict."""
    solid = build_pawn().val()
    points, triangles = solid.tessellate(solid_tolerance, ANGULAR_DEFLECTION)

    verts, tris = weld(points, triangles)
    normals = face_normals(verts, tris)
    group = smooth_groups(tris, normals)
    out_verts, out_normals, out_tris = vertex_normals(verts, tris, normals, group)

    bbox = solid.BoundingBox()
    return {
        "meta": {
            "name": "Chess pawn",
            "units": "mm",
            "up": "z",
            "height": TOTAL_HEIGHT,
            "baseDiameter": 2 * BASE_RADIUS,
            "headDiameter": 2 * HEAD_RADIUS,
            "volumeMm3": round(solid.Volume(), 2),
            "sourceFaces": len(solid.Faces()),
            "deflectionMm": solid_tolerance,
            "creaseAngleDeg": round(math.degrees(CREASE_ANGLE), 1),
            "generatedBy": "export_pawn_mesh.py (CadQuery/OpenCascade)",
        },
        "position": [round(c, 5) for v in out_verts for c in v],
        "normal": [round(c, 5) for v in out_normals for c in v],
        "index": [i for tri in out_tris for i in tri],
        "bboxMin": [bbox.xmin, bbox.ymin, bbox.zmin],
        "bboxMax": [bbox.xmax, bbox.ymax, bbox.zmax],
    }


def main() -> None:
    """Write docs/pawn.json and report how big it came out."""
    payload = build_mesh()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")

    verts = len(payload["position"]) // 3
    tris = len(payload["index"]) // 3
    size_kb = OUT_PATH.stat().st_size / 1024
    print(f"wrote {OUT_PATH.relative_to(OUT_PATH.parent.parent)}")
    print(f"  vertices:    {verts}")
    print(f"  triangles:   {tris}")
    print(f"  file size:   {size_kb:.1f} KiB")
    print(f"  dimensions:  {payload['meta']['baseDiameter']:.1f} x {payload['meta']['height']:.1f} mm")


if __name__ == "__main__":
    main()
