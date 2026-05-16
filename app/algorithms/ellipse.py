from typing import List, Tuple 

Points = List[Tuple[int, int]] 

def _plot_4_symmetric(cx:int, cy:int, x:int, y:int) -> Points:
    return [
        (cx + x, cy + y), (cx - x, cy + y),
        (cx + x, cy - y), (cx - x, cy - y),
    ] 

def midpoint_ellipse(cx:int, cy:int, rx:int, ry:int) -> Points:
    if rx <= 0 or ry <= 0:
        return [(cx, cy)]
    points = []
    rx2, ry2 = rx * rx, ry * ry
    x, y = 0, ry
    # ── Region 1 ────────────────────────────────────────────────────
    p1 = ry2 - rx2 * ry + 0.25 * rx2
    while 2 * ry2 * x < 2 * rx2 * y:
        points.extend(_plot_4_symmetric(cx, cy, x, y))
        x += 1
        if p1 < 0:
            p1 += 2 * ry2 * x + ry2
        else:
            y -= 1
            p1 += 2 * ry2 * x - 2 * rx2 * y + ry2
    # ── Region 2 ────────────────────────────────────────────────────
    p2 = ry2 * (x + 0.5) ** 2 + rx2 * (y - 1) ** 2 - rx2 * ry2
    while y >= 0:
        points.extend(_plot_4_symmetric(cx, cy, x, y))
        y -= 1
        if p2 > 0:
            p2 += rx2 - 2 * rx2 * y
        else:
            x += 1
            p2 += 2 * ry2 * x - 2 * rx2 * y + rx2
    return points

def bresenham_ellipse(cx: int, cy: int, rx: int, ry: int) -> Points:
    if rx <= 0 or ry <= 0:
        return [(cx, cy)]
    points = []
    rx2, ry2 = rx * rx, ry * ry
    two_rx2, two_ry2 = 2 * rx2, 2 * ry2
    x, y = 0, ry
    dx, dy = 0, two_rx2 * y
    # ── Region 1 ────────────────────────────────────────────────────
    p = round(ry2 - rx2 * ry + 0.25 * rx2)
    while dx < dy:
        points.extend(_plot_4_symmetric(cx, cy, x, y))
        x += 1
        dx += two_ry2
        if p < 0:
            p += ry2 + dx
        else:
            y -= 1
            dy -= two_rx2
            p += ry2 + dx - dy
    # ── Region 2 ────────────────────────────────────────────────────
    p = round(ry2 * (x + 0.5) ** 2 + rx2 * (y - 1) ** 2 - rx2 * ry2)
    while y >= 0:
        points.extend(_plot_4_symmetric(cx, cy, x, y))
        y -= 1
        dy -= two_rx2
        if p > 0:
            p += rx2 - dy
        else:
            x += 1
            dx += two_ry2
            p += rx2 - dy + dx
    return points