from collections import deque
from typing import List, Tuple 

Points = List[Tuple[int, int]] 

def bfs(
    pixels: list, 
    width: int, 
    height: int, 
    x:int, 
    y:int, 
    target_color:int, 
    fill_color:int,
) -> Points: 
    if target_color == fill_color:
        return []
    filled = []
    visited = bytearray(width * height)  
    queue = deque()
    queue.append((x, y))

    while queue:
        cx, cy = queue.popleft()
        if cx < 0 or cy < 0 or cx >= width or cy >= height:
            continue
        idx = cy * width + cx
        if visited[idx]:
            continue
        visited[idx] = 1
        if pixels(cx, cy) != target_color:
            continue
        filled.append((cx, cy))
        queue.append((cx + 1, cy))
        queue.append((cx - 1, cy))
        queue.append((cx, cy + 1))
        queue.append((cx, cy - 1))
    return filled