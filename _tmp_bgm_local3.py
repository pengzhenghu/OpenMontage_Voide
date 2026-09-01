# -*- coding: utf-8 -*-
"""v3 BGM 后备方案：numpy 本地合成古筝风纯音乐（Karplus-Strong 拨弦 + 五声音阶）。
所有云端音乐 API key 均无效，改用离线合成；输出 84s，供 stage3 atrim 到成片时长。"""
import subprocess
from pathlib import Path

import numpy as np

SR = 44100
OUT_WAV = Path("projects/jinan-springs/assets/audio/_bgm_classical_raw.wav")
OUT_MP3 = Path("projects/jinan-springs/assets/audio/bgm_jinan_classical.mp3")
TOTAL = 84.0
rng = np.random.default_rng(42)


def pluck(freq, dur, vel=1.0):
    """Karplus-Strong 拨弦（分块向量化）：模拟古筝弹拨音色。"""
    N = max(2, int(round(SR / freq)))
    buf = rng.uniform(-1, 1, N).astype(np.float64)
    n_out = int(SR * dur)
    out = np.empty(n_out)
    damp = 0.9972 - min(0.0028, freq * 1.5e-6)  # 低音延音更长
    i = 0
    while i < n_out:
        j = min(i + N, n_out)          # 每块 ≤N 个样本，循环内索引安全
        idx = (i + np.arange(j - i)) % N
        out[i:j] = buf[idx]
        avg = 0.5 * (buf[idx] + buf[(idx + 1) % N])
        buf[idx] = damp * avg
        i = j
    x = out
    # 拨弦瞬态：快起音 + 指数衰减
    atk = np.minimum(1.0, np.arange(n_out) / (0.004 * SR))
    env = atk * np.exp(-np.arange(n_out) / (SR * dur * 0.42))
    x *= env * vel
    return x / (np.abs(x).max() + 1e-9) * vel


def place(buf, t, sig, pan):
    i0 = int(t * SR)
    i1 = min(len(buf), i0 + len(sig))
    if i0 >= len(buf) or i1 <= i0:
        return
    seg = sig[: i1 - i0]
    buf[i0:i1, 0] += seg * (1.0 - 0.55 * pan)
    buf[i0:i1, 1] += seg * (0.45 + 0.55 * pan)


# ---- 五声音阶（宫商角徵羽），C 宫 ----
def pent(degree):
    """degree: 0=C4 起，按五声音阶上下取音。"""
    base = 261.626
    steps = [0, 2, 4, 7, 9]
    octv, idx = divmod(degree, 5)
    return base * (2.0 ** ((steps[idx] + 12 * octv) / 12.0))


BEAT = 0.80  # ~75bpm，悠缓
notes = []   # (time, freq, dur, vel, pan)

# 低音铺底：每句头一个低八度长音
phrase_starts = [0.5, 8.5, 16.5, 24.5, 32.5, 40.5, 48.5, 56.5, 64.5, 72.0]
for i, ts in enumerate(phrase_starts):
    deg = [-10, -8, -7, -5, -10, -7, -5, -8, -10, -12][i]
    notes.append((ts, pent(deg), 6.5, 0.55, 0.5))

# 主旋律：五声级进 + 偶尔跳进，每句尾留白（中国式的空灵）
t = 1.5
deg = 0
end_melody = 76.0
while t < end_melody:
    if rng.random() < 0.72:  # 留白概率，制造疏密
        r = rng.random()
        step = rng.choice([-2, -1, -1, 1, 1, 2]) if r > 0.25 else rng.choice([-3, 3, -4, 4])
        deg = int(np.clip(deg + step, -3, 9))
        vel = float(rng.uniform(0.5, 0.85))
        dur = BEAT * float(rng.choice([1.0, 1.0, 1.5, 2.0, 0.5]))
        pan = float(np.clip(0.5 + deg * 0.06 + rng.uniform(-0.08, 0.08), 0, 1))
        notes.append((t, pent(deg), dur + 1.6, vel, pan))
        # 偶尔加一个高八度回声轻拨
        if rng.random() < 0.18:
            notes.append((t + BEAT * 0.5, pent(deg + 5), dur + 1.0, vel * 0.28, 1 - pan))
        t += dur
    else:
        t += BEAT * float(rng.choice([1.0, 2.0]))

# 中段一处琶音瀑布（40s 附近），上行五声扫弦
for k in range(6):
    notes.append((40.5 + k * 0.11, pent(-3 + k), 3.5, 0.42 - k * 0.02, k / 5.0))

# 尾句：渐稀的三个音
for k, (tt, d) in enumerate([(76.0, 0), (77.6, 2), (79.4, -3)]):
    notes.append((tt, pent(d), 4.5, 0.5 - k * 0.12, 0.5))

buf = np.zeros((int(TOTAL * SR), 2))
for t0, f, d, v, p in notes:
    place(buf, t0, pluck(f, d, v), p)

# 简易混响：多抽头延迟反馈
dly = int(0.13 * SR)
wet = np.zeros_like(buf)
acc = np.zeros_like(buf)
for k in range(6):
    acc += np.roll(buf, dly * (k + 1), axis=0) * (0.45 ** (k + 1))
wet = acc
mix = buf * 0.85 + wet * 0.5

# 整体包络：淡入 2.5s / 淡出 5s
n = len(mix)
fade_in = np.minimum(1.0, np.arange(n) / (2.5 * SR))
fade_out = np.minimum(1.0, np.arange(n)[::-1] / (5.0 * SR))
mix *= (fade_in * fade_out)[:, None]

# 软限幅归一
peak = np.abs(mix).max()
mix = np.tanh(mix / peak * 1.15) * 0.9

pcm = (mix * 32767).astype(np.int16)

OUT_WAV.parent.mkdir(parents=True, exist_ok=True)
import wave
with wave.open(str(OUT_WAV), "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(44100)
    w.writeframes(pcm.tobytes())

r = subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(OUT_WAV),
                    "-c:a", "libmp3lame", "-b:a", "192k", str(OUT_MP3)],
                   capture_output=True)
if r.returncode != 0:
    print("mp3 FAIL", (r.stderr or b"").decode("utf-8", "ignore")[-400:])
else:
    OUT_WAV.unlink()
    print("BGM ok ->", OUT_MP3)
