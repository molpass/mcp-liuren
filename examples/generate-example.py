# -*- coding: utf-8 -*-
"""예제 천지반 생성 (고정 일시 → 결정론적 재현).
실행: ../.venv/Scripts/python.exe examples/generate-example.py  (repo 루트에서)
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding="utf-8")

from datetime import datetime
from liuren_core import divine, format_text, render_png

# 샘플: 2024-02-10 14:30 (갑진년 설날, 日干支 甲辰 — JDN/만세력 교차검증 완료)
dt = datetime(2024, 2, 10, 14, 30)
result = divine(dt)
print(format_text(result))

png = render_png(result)
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "liuren_example.png")
with open(out, "wb") as f:
    f.write(png)
print(f"\nwrote {out} ({len(png)} bytes)")
