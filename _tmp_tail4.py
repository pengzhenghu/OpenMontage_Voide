# -*- coding: utf-8 -*-
"""v4 结尾渐变验证：全解码 + 末 8s 逐秒 RMS。"""
import subprocess
from pathlib import Path

import numpy as np

F = Path("projects/jinan-springs/renders/jinan_springs_final_v4.mp4")
r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(F), "-f", "null", "-"],
                   capture_output=True)
print("DECODE:", "OK" if r.returncode == 0 else "FAIL")
r = subprocess.run(["ffmpeg", "-v", "error", "-ss", "64.7", "-i", str(F),
                    "-f", "s16le", "-ac", "1", "-ar", "22050", "-"],
                   capture_output=True)
a = np.frombuffer(r.stdout, np.int16).astype(np.float64) / 32768
n = 22050
for s in range(len(a) // n):
    seg = a[s * n:(s + 1) * n]
    print(f"t={64.7 + s:5.1f}s  RMS={20 * np.log10(np.sqrt(np.mean(seg ** 2)) + 1e-7):6.1f} dB")
