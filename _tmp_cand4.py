# -*- coding: utf-8 -*-
"""v4：为 18s 芙蓉街 / 43s 红船 扫描更清晰候选；定位 132334 墙字“济南”。"""
import subprocess
from pathlib import Path

import numpy as np

ROOT = Path("projects/_inbox")
OUT = Path("projects/jinan-springs/review_frames")
OUT.mkdir(parents=True, exist_ok=True)

FURONG = [("芙蓉街", "p4p/DJI_20260814135422_0148_D.MP4", 3),
          ("芙蓉街", "p4p/DJI_20260814135442_0149_D.MP4", 3),
          ("芙蓉街", "p4p/DJI_20260814135531_0150_D.MP4", 3),
          ("芙蓉街", "p4p/DJI_20260814135723_0153_D.MP4", 3),
          ("芙蓉街", "p4p/DJI_20260814135844_0154_D.MP4", 3),
          ("芙蓉街", "p4p/DJI_20260814140541_0155_D.MP4", 3),
          ("芙蓉街", "p4p/DJI_20260814140553_0156_D.MP4", 3),
          ("芙蓉街", "p4p/DJI_20260814140603_0157_D.MP4", 3),
          ("芙蓉街", "p4p/DJI_20260814140732_0158_D.MP4", 3),
          ("芙蓉街", "360l/2026-08-14 140156.mp4", 5),
          ("芙蓉街", "360l/2026-08-14 140327.mp4", 5),
          ("芙蓉街", "360l/2026-08-14 140230.mp4", 7)]

DAMING = [("大明湖", "p4p/DJI_20260814122935_0097_D.MP4", 3),
          ("大明湖", "p4p/DJI_20260814123002_0098_D.MP4", 3),
          ("大明湖", "p4p/DJI_20260814123605_0099_D.MP4", 3),
          ("大明湖", "p4p/DJI_20260814123914_0101_D.MP4", 3),
          ("大明湖", "p4p/DJI_20260814123943_0103_D.MP4", 3),
          ("大明湖", "p4p/DJI_20260814124029_0104_D.MP4", 3),
          ("大明湖", "p4p/DJI_20260814124101_0105_D.MP4", 3),
          ("大明湖", "p4p/DJI_20260814124120_0106_D.MP4", 3),
          ("大明湖", "360l/2026-08-14 122444.mp4", 10),
          ("大明湖", "360l/2026-08-14 122524.mp4", 3),
          ("大明湖", "360l/2026-08-14 122544.mp4", 3),
          ("大明湖", "360l/2026-08-14 122557.mp4", 3)]


def _vstream_dur(loc, clip):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                        "-show_entries", "stream=duration", "-of", "csv=p=0",
                        str(ROOT / loc / clip)], capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def sharp(loc, clip, t):
    t = min(t, max(0.0, _vstream_dur(loc, clip) - 0.2))
    r = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.2f}", "-i", str(ROOT / loc / clip),
                        "-frames:v", "1", "-vf", "scale=540:960,format=gray",
                        "-f", "rawvideo", "-"], capture_output=True)
    a = np.frombuffer(r.stdout, np.uint8).astype(np.float64).reshape(960, 540)
    lap = (a[1:-1, :-2] + a[1:-1, 2:] + a[:-2, 1:-1] + a[2:, 1:-1] - 4 * a[1:-1, 1:-1])
    return float(np.var(lap))


def grab(loc, clip, t, out):
    t = min(t, max(0.0, _vstream_dur(loc, clip) - 0.2))
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{t:.2f}", "-i", str(ROOT / loc / clip),
                    "-frames:v", "1", "-vf", "scale=270:480", str(out)],
                   capture_output=True)


def sheet(items, name):
    cells, vals = [], []
    for k, (loc, clip, t) in enumerate(items):
        p = OUT / f"_v4c_{name}_{k:02d}.jpg"
        grab(loc, clip, t, p)
        cells.append(p)
        vals.append((k, Path(clip).stem[:14], round(sharp(loc, clip, t), 1)))
    n = len(cells)
    cols, rows = 4, (n + 3) // 4
    while n < cols * rows:
        bk = OUT / f"_v4c_{name}_blk{n}.jpg"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i",
                        "color=c=black:s=270x480", "-frames:v", "1", str(bk)],
                       capture_output=True)
        cells.append(bk)
        n += 1
    ins = [a for p in cells for a in ("-i", str(p))]
    lay = "|".join(f"{c*270}_{r*480}" for r in range(rows) for c in range(cols))
    fc = "".join(f"[{i}:v]" for i in range(len(cells))) + \
         f"xstack=inputs={len(cells)}:layout={lay}[o]"
    subprocess.run(["ffmpeg", "-y", "-v", "error"] + ins +
                   ["-filter_complex", fc, "-map", "[o]", str(OUT / f"v4_sheet_{name}.jpg")],
                   capture_output=True)
    print(name, sorted(vals, key=lambda x: -x[2]))


sheet(FURONG, "furong")
sheet(DAMING, "daming")

# 132334 墙字定位：全幅缩略帧
for k, t in enumerate([0.5, 1.08, 1.8, 2.6, 3.2]):
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", str(t),
                    "-i", str(ROOT / "曲水亭街+百花洲" / "360l/2026-08-14 132334.mp4"),
                    "-frames:v", "1", "-vf", "scale=1280:-2",
                    str(OUT / f"v4_wall_{k}.jpg")], capture_output=True)
print("wall frames ok")
