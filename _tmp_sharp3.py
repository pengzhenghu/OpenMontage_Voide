# -*- coding: utf-8 -*-
"""v3: 量化 27 个已渲镜头的清晰度（拉普拉斯方差）。"""
import subprocess
from pathlib import Path
import numpy as np

W = Path("projects/jinan-springs/work")
rows = []
for i in range(27):
    p = W / f"shot{i:02d}.mp4"
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(p), "-vf",
         "fps=2,scale=540:960,format=gray", "-f", "rawvideo", "-"],
        capture_output=True).stdout
    n = len(raw) // (540 * 960)
    vals = []
    for f in range(n):
        img = np.frombuffer(raw[f * 540 * 960:(f + 1) * 540 * 960],
                            np.uint8).reshape(960, 540).astype(np.float64)
        lap = (img[:-2, 1:-1] + img[2:, 1:-1] + img[1:-1, :-2] + img[1:-1, 2:]
               - 4 * img[1:-1, 1:-1])
        vals.append(lap.var())
    rows.append((np.median(vals), i))
for med, i in sorted(rows):
    print(f"shot{i:02d}  sharp={med:8.1f}")
