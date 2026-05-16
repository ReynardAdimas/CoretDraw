from typing import List, Tuple 

Points = List[Tuple[int, int]] 

def _plot_8_symmetric(cx:int, cy:int, x:int, y:int) -> Points:
    return [
        (cx + x, cy + y), (cx - x, cy + y),
        (cx + x, cy - y), (cx - x, cy - y),
        (cx + y, cy + x), (cx - y, cy + x),
        (cx + y, cy - x), (cx - y, cy - x),
    ] 

def midpoint_circle(cx:int, cy:int, r:int) -> Points:
    if r <= 0:
        return [(cx, cy)]
    points = []
    x, y = 0, r
    p = 1 - r  
    points.extend(_plot_8_symmetric(cx, cy, x, y))
    while x < y:
        x += 1
        if p < 0:
            p += 2 * x + 1
        else:
            y -= 1
            p += 2 * (x - y) + 1
        points.extend(_plot_8_symmetric(cx, cy, x, y))
    return points 

def bresenham_circle(cx:int, cy:int, r:int) -> Points:
    if r <= 0:
        return [(cx, cy)]
    points = []
    x, y = 0, r
    d = 3 - 2 * r  
    points.extend(_plot_8_symmetric(cx, cy, x, y))
    while x <= y:
        x += 1
        if d < 0:
            d += 4 * x + 6
        else:
            y -= 1
            d += 4 * (x - y) + 10
        points.extend(_plot_8_symmetric(cx, cy, x, y))
    return points