# -*- coding: utf-8 -*-
"""v4 自验：时长/像素格式/全解码/PTS + 18s、43s 清晰度 + 黄昏亮度。"""
import subprocess
from pathlib import Path

import numpy as np

F = Path("projects/jinan-springs/renders/jinan_springs_final_v4.mp4")
OUT = Path("projects/jinan-springs/review_frames")

# 1) 基本信息
r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                    "-show_entries", "stream=width,height,pix_fmt:format=duration",
                    "-of", "default=nw=1", str(F)], capture_output=True, text=True)
print("PROBE:\n" + r.stdout)

# 2) 全解码
r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(F), "-f", "null", "-"],
                   capture_output=True)
print("DECODE:", "OK" if r.returncode == 0 else
      "FAIL " + r.stderr.decode("utf-8", "ignore")[-300:])

# 3) PTS 连续性（排序后校验，B 帧解码序会乱）
r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                    "-show_entries", "packet=pts_time", "-of", "csv=p=0", str(F)],
                   capture_output=True, text=True)
pts = sorted(float(x) for x in r.stdout.split() if x)
jumps = [(round(pts[i - 1], 3), round(pts[i], 3))
         for i in range(1, len(pts)) if abs(pts[i] - pts[i - 1]) > 0.12]
print(f"PTS: n={len(pts)} last={pts[-1]:.2f} bad_jumps={len(jumps)}")


def frame_gray(t):
    r = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.2f}", "-i", str(F),
                        "-frames:v", "1", "-vf", "scale=540:960,format=gray",
                        "-f", "rawvideo", "-"], capture_output=True)
    return np.frombuffer(r.stdout, np.uint8).astype(np.float64).reshape(960, 540)


def sharp(a):
    lap = (a[1:-1, :-2] + a[1:-1, 2:] + a[:-2, 1:-1] + a[2:, 1:-1] - 4 * a[1:-1, 1:-1])
    return float(np.var(lap))


# 4) 抽帧：18s 芙蓉街 / 43s 红船 / 55-65 黄昏 / 65.8“济” / 67.3“南” / 70 收尾
for t in [18.0, 43.0, 55.0, 60.0, 65.8, 67.3, 70.0]:
    a = frame_gray(t)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{t:.2f}", "-i", str(F),
                    "-frames:v", "1", str(OUT / f"v4f_{t:g}.jpg")], capture_output=True)
    print(f"t={t:5.1f}  sharp={sharp(a):8.1f}  mean={a.mean():5.1f}")
print("frames -> review_frames/v4f_*.jpg")
