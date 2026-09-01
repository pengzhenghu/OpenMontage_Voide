# -*- coding: utf-8 -*-
"""v3: 为模糊镜头扫描候选片段，输出每景点 4x3 联系表 + 清晰度值。"""
import subprocess
from pathlib import Path
import numpy as np

ROOT = Path("projects/_inbox")
OUT = Path("projects/jinan-springs/review_frames")
OUT.mkdir(parents=True, exist_ok=True)

CANDS = {
    "furong": [
        ("芙蓉街", "360l/2026-08-14 135421.mp4", 3.6),
        ("芙蓉街", "360l/2026-08-14 140230.mp4", 7.0),
        ("芙蓉街", "360l/2026-08-14 140230.mp4", 9.5),
        ("芙蓉街", "p4p/DJI_20260814135531_0150_D.MP4", 3.0),
        ("芙蓉街", "p4p/DJI_20260814135531_0150_D.MP4", 8.0),
        ("芙蓉街", "p4p/DJI_20260814135723_0153_D.MP4", 2.0),
        ("芙蓉街", "p4p/DJI_20260814135844_0154_D.MP4", 3.0),
        ("芙蓉街", "p4p/DJI_20260814140553_0156_D.MP4", 3.0),
        ("芙蓉街", "p4p/DJI_20260814140603_0157_D.MP4", 3.0),
        ("芙蓉街", "p4p/DJI_20260814140732_0158_D.MP4", 5.0),
        ("芙蓉街", "360l/2026-08-14 140156.mp4", 5.0),
        ("芙蓉街", "360l/2026-08-14 140327.mp4", 5.0),
    ],
    "baotu": [
        ("趵突泉", "p4p/DJI_20260814150556_0174_D.MP4", 3.0),
        ("趵突泉", "p4p/DJI_20260814150747_0177_D.MP4", 3.0),
        ("趵突泉", "p4p/DJI_20260814150803_0178_D.MP4", 3.0),
        ("趵突泉", "p4p/DJI_20260814151009_0180_D.MP4", 3.0),
        ("趵突泉", "p4p/DJI_20260814151042_0182_D.MP4", 3.0),
        ("趵突泉", "p4p/DJI_20260814151131_0185_D.MP4", 2.0),
        ("趵突泉", "p4p/DJI_20260814151145_0186_D.MP4", 4.0),
        ("趵突泉", "p4p/DJI_20260814151352_0188_D.MP4", 4.0),
        ("趵突泉", "p4p/DJI_20260814151814_0190_D.MP4", 4.0),
        ("趵突泉", "p4p/DJI_20260814152003_0192_D.MP4", 4.0),
        ("趵突泉", "p4p/DJI_20260814152210_0195_D.MP4", 5.0),
        ("趵突泉", "p4p/DJI_20260814152603_0201_D.MP4", 5.0),
    ],
    "daming": [
        ("大明湖", "360l/2026-08-14 122444.mp4", 6.0),
        ("大明湖", "360l/2026-08-14 122444.mp4", 10.0),
        ("大明湖", "360l/2026-08-14 122444.mp4", 18.0),
        ("大明湖", "p4p/DJI_20260814123943_0103_D.MP4", 3.0),
        ("大明湖", "p4p/DJI_20260814124029_0104_D.MP4", 4.0),
        ("大明湖", "p4p/DJI_20260814124101_0105_D.MP4", 4.0),
    ],
    "quancheng": [
        ("泉城广场", "p4p/DJI_20260814142847_0161_D.MP4", 3.0),
        ("泉城广场", "p4p/DJI_20260814143019_0162_D.MP4", 4.0),
        ("泉城广场", "p4p/DJI_20260814143810_0163_D.MP4", 3.0),
        ("泉城广场", "p4p/DJI_20260814143920_0164_D.MP4", 3.0),
        ("泉城广场", "p4p/DJI_20260814143957_0166_D.MP4", 2.0),
        ("泉城广场", "p4p/DJI_20260814144430_0167_D.MP4", 4.0),
        ("泉城广场", "p4p/DJI_20260814144445_0168_D.MP4", 4.0),
        ("泉城广场", "p4p/DJI_20260814144502_0169_D.MP4", 4.0),
        ("泉城广场", "p4p/DJI_20260814144526_0170_D.MP4", 4.0),
        ("泉城广场", "p4p/DJI_20260814144834_0171_D.MP4", 4.0),
        ("泉城广场", "360l/2026-08-14 144337.mp4", 7.0),
        ("泉城广场", "360l/2026-08-14 143440.mp4", 4.0),
    ],
}


def sharp_of(raw):
    img = np.frombuffer(raw, np.uint8).reshape(960, 540).astype(np.float64)
    lap = (img[:-2, 1:-1] + img[2:, 1:-1] + img[1:-1, :-2] + img[1:-1, 2:]
           - 4 * img[1:-1, 1:-1])
    return lap.var()


for loc_key, cands in CANDS.items():
    frames = []
    for i, (loc, clip, ts) in enumerate(cands):
        src = ROOT / loc / clip
        r = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(ts), "-i", str(src),
                            "-frames:v", "1", "-f", "rawvideo",
                            "-vf", "scale=540:960,format=gray", "-"],
                           capture_output=True)
        sv = sharp_of(r.stdout) if len(r.stdout) >= 540 * 960 else -1.0
        r2 = subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", str(ts), "-i", str(src),
                             "-frames:v", "1", "-vf", "scale=270:480", "-q:v", "3",
                             str(OUT / f"_c_{loc_key}_{i:02d}.jpg")],
                            capture_output=True)
        frames.append(sv)
        print(f"{loc_key}{i:02d}  {Path(clip).stem} @{ts}  sharp={sv:8.1f}")
    # tile 4x3 (不足补黑块用最后一个)
    n = len(cands)
    while n % 4 != 0:
        n += 1
    cmd = ["ffmpeg", "-y", "-v", "error"]
    for i in range(len(cands)):
        cmd += ["-i", str(OUT / f"_c_{loc_key}_{i:02d}.jpg")]
    if len(cands) < n:
        cmd += ["-f", "lavfi", "-i", "color=c=black:s=270x480:d=1"]
    fc = "".join(f"[{i}:v]" for i in range(n)) + f"xstack=inputs={n}:layout="
    pos = []
    for r in range(n // 4):
        for c in range(4):
            pos.append(f"{c*270}_{r*480}")
    fc += "|".join(pos)
    cmd += ["-filter_complex", fc, "-frames:v", "1", "-q:v", "3",
            str(OUT / f"v3_sheet_{loc_key}.jpg")]
    r = subprocess.run(cmd, capture_output=True)
    print(loc_key, "sheet rc=", r.returncode)
