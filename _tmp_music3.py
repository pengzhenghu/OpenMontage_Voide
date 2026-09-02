# -*- coding: utf-8 -*-
"""v3: ElevenLabs Music 生成中国古典风 BGM（古筝主奏）。"""
import json
import re
import sys
from pathlib import Path

import requests

raw = Path(".env").read_bytes()
env_txt = None
for enc in ("utf-8-sig", "utf-16", "utf-8"):
    try:
        env_txt = raw.decode(enc)
        if "ELEVENLABS_API_KEY" in env_txt:
            break
    except UnicodeDecodeError:
        continue
m = re.search(r"ELEVENLABS_API_KEY\s*=\s*([^\r\n]+)", env_txt)
key = m.group(1).strip().strip('"').strip("'")

prompt = ("Traditional Chinese classical instrumental underscore. Gentle guzheng "
          "(Chinese zither) lead playing a flowing pentatonic melody, soft erhu and "
          "dizi flute accents, sparse guqin-like plucks, light wooden percussion only "
          "in the second half. Serene, elegant, nostalgic, like spring water flowing "
          "through an old town. Cinematic, warm, no vocals, no modern drums, no synths.")

r = requests.post("https://api.elevenlabs.io/v1/music",
                  headers={"xi-api-key": key, "Content-Type": "application/json"},
                  json={"prompt": prompt, "music_length_ms": 75000}, timeout=300)
print("status", r.status_code)
if r.status_code != 200:
    print(r.text[:600])
    sys.exit(1)
out = Path("projects/jinan-springs/assets/audio/bgm_jinan_classical.mp3")
out.write_bytes(r.content)
print("saved", out, len(r.content))
