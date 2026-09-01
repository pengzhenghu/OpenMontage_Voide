# -*- coding: utf-8 -*-
"""v3: Suno 生成中国古典风纯音乐 BGM。"""
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(".").resolve()))

raw = Path(".env").read_bytes()
for enc in ("utf-8-sig", "utf-16", "utf-8"):
    try:
        txt = raw.decode(enc)
        if "SUNO_API_KEY" in txt:
            break
    except UnicodeDecodeError:
        continue
for m in re.finditer(r"([A-Z0-9_]+)\s*=\s*([^\r\n]+)", txt):
    os.environ.setdefault(m.group(1), m.group(2).strip().strip('"').strip("'"))

from tools.audio.suno_music import SunoMusic

t = SunoMusic()
r = t.execute({
    "prompt": ("Serene traditional Chinese classical instrumental. Guzheng (Chinese "
               "zither) leading a flowing pentatonic melody, gentle erhu and bamboo "
               "dizi flute accents, sparse elegant plucks, like spring water flowing "
               "through an ancient town. Calm, warm, nostalgic, cinematic underscore. "
               "No vocals, no drums, no electronic sounds."),
    "instrumental": True,
    "model": "V4_5",
    "output_path": "projects/jinan-springs/assets/audio/bgm_jinan_classical.mp3",
})
print("success:", r.success)
if r.success:
    print(r.data.get("title"), r.data.get("duration_seconds"), r.data.get("output"))
else:
    print("ERR:", r.error)
