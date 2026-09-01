# -*- coding: utf-8 -*-
"""v5 横屏自验：probe 尺寸/时长 + 全解码 + PTS 连续性 + 关键帧 sharp/mean 抽帧目检。"""
import subprocess
from pathlib import Path

import numpy as np

F = Path("projects/jinan-springs/renders/jinan_springs_final_v5.mp4")
OUT = Path("projects/jinan-springs/review_frames")

r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                    "-show_entries", "stream=width,height,pix_fmt",
                    "-show_entries", "format=duration",
                    "-of", "default=noprint_wrappers=1", str(F)],
                   capture_output=True, text=True)
print("PROBE:", r.stdout.replace("\n", " | "))

r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(F), "-f", "null", "-"],
                   capture_output=True)
print("DECODE:", "OK" if r.returncode == 0 else "FAIL")

# PTS 连续性
r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                    "-show_entries", "frame=pts_time", "-of", "csv=p=0", str(F)],
                   capture_output=True, text=True)
pts = [float(x.rstrip(",")) for x in r.stdout.split() if x.rstrip(",")]
jumps = [round(pts[i] - pts[i - 1], 3) for i in range(1, len(pts))
         if abs(pts[i] - pts[i - 1]) > 0.12]
print(f"PTS n={len(pts)} bad_jumps={len(jumps)} {jumps[:5]}")

# 关键帧 sharp + mean
for t in [3, 18, 43, 44.5, 55, 60, 65.8, 67.3, 70]:
    r = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t}", "-i", str(F),
                        "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "gray", "-"],
                       capture_output=True)
    a = np.frombuffer(r.stdout, np.uint8).astype(np.float64)
    if a.size == 0:
        print(f"t={t} EMPTY")
        continue
    g = a.reshape(1080, 1920)
    lap = (g[1:-1, 2:] + g[1:-1, :-2] + g[2:, 1:-1] + g[:-2, 1:-1] - 4 * g[1:-1, 1:-1])
    print(f"t={t:5.1f}  sharp={lap.var():7.1f}  mean={g.mean():6.1f}")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{t}", "-i", str(F),
                    "-frames:v", "1", str(OUT / f"v5f_{t}.jpg")],
                   capture_output=True)
print("FRAMES SAVED")
