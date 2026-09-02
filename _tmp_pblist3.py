# -*- coding: utf-8 -*-
"""v3: Pixabay 古筝曲目列表（不下载，先列候选）。"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(".").resolve()))
from tools.audio.pixabay_music import PixabayMusic

t = PixabayMusic()
tracks = t._search({"query": "guzheng chinese traditional"})
for i, tr in enumerate(tracks[:20]):
    print(i, tr.get("title"), tr.get("artist"), tr.get("duration"), tr.get("audio_url")[:80])
