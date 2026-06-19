# -*- coding: utf-8 -*-
"""대육임(大六壬) 핵심 로직: 달력 변환(일시→간지/절기) + kinliuren 점단 + 텍스트/PNG 렌더.

kinliuren은 간지·절기를 스스로 계산하지 않으므로, lunar_python으로
(節氣, 農曆月, 日干支, 時干支)를 산출해 주입하는 '달력 레이어'를 둔다.
일시 변환은 결정론적이며 day 간지는 JDN 공식과 교차검증되었다.
"""
from __future__ import annotations

import io
import os
import re
from datetime import datetime

from lunar_python import Solar
from kinliuren import kinliuren
from PIL import Image as PILImage, ImageDraw, ImageFont

# lunar_python(간체 일부) → kinliuren(번체) 절기명 보정
_S2T = {"惊蛰": "驚蟄", "谷雨": "穀雨", "小满": "小滿", "芒种": "芒種", "处暑": "處暑"}

# 12지지 → 4×4 그리드 위치 (전통 정사각 명반 배치). 중앙 2×2는 정보패널.
#  [巳][午][未][申]
#  [辰][      ][酉]
#  [卯][ info ][戌]
#  [寅][丑][子][亥]
_BRANCH_CELL = {
    "寅": (3, 0), "卯": (2, 0), "辰": (1, 0), "巳": (0, 0),
    "午": (0, 1), "未": (0, 2), "申": (0, 3), "酉": (1, 3),
    "戌": (2, 3), "亥": (3, 3), "子": (3, 2), "丑": (3, 1),
}


def to_ganzhi(dt: datetime) -> dict:
    """일시 → (節氣, 農曆月, 日干支, 時干支). 번체 절기명으로 반환."""
    lunar = Solar.fromYmdHms(dt.year, dt.month, dt.day, dt.hour, dt.minute, 0).getLunar()
    jq = lunar.getPrevJieQi().getName()  # 점단 시각에 유효한 직전 절기(月將 결정)
    jq = _S2T.get(jq, jq)
    return {
        "jieqi": jq,
        "cmonth": abs(lunar.getMonth()),
        "dayGanzhi": lunar.getDayInGanZhi(),
        "hourGanzhi": lunar.getTimeInGanZhi(),
    }


def divine(dt: datetime | None, manual: dict | None = None) -> dict:
    """간지를 구해 kinliuren 점단 결과(dict)를 반환. manual 제공 시 변환 생략."""
    if manual:
        need = ("jieqi", "cmonth", "dayGanzhi", "hourGanzhi")
        missing = [k for k in need if not manual.get(k)]
        if missing:
            raise ValueError(f"manualGanzhi 누락 키: {', '.join(missing)} (필요: {', '.join(need)})")
        gz = {
            "jieqi": _S2T.get(manual["jieqi"], manual["jieqi"]),
            "cmonth": int(manual["cmonth"]),
            "dayGanzhi": manual["dayGanzhi"],
            "hourGanzhi": manual["hourGanzhi"],
        }
        source = "manual"
    else:
        if dt is None:
            raise ValueError("datetime 또는 manualGanzhi 중 하나는 필요합니다.")
        gz = to_ganzhi(dt)
        source = "calendar"

    plate = kinliuren.Liuren(gz["jieqi"], gz["cmonth"], gz["dayGanzhi"], gz["hourGanzhi"]).result(0)
    plate["_input"] = {**gz, "source": source, "datetime": dt.strftime("%Y-%m-%d %H:%M") if dt else None}
    return plate


def format_text(r: dict) -> str:
    inp = r.get("_input", {})
    lines = [
        "대육임(大六壬) 점단",
        f"일시: {inp.get('datetime') or '(수동 간지)'}  |  節氣 {r.get('節氣')}  農曆 {r.get('農曆月')}월",
        f"日期: {r.get('日期')}",
        f"格局: {' / '.join(r.get('格局', [])) or '-'}    日馬(신살): {r.get('日馬', '-')}",
        "",
        "[三傳]",
    ]
    sp = r.get("三傳", {})
    for k in ("初傳", "中傳", "末傳"):
        v = sp.get(k)
        if v:
            lines.append(f"  {k}: {v[0]}  天將 {v[1]}  六親 {v[2]}  遁干 {v[3]}")
    lines.append("")
    lines.append("[四課]")
    sk = r.get("四課", {})
    for k in ("一課", "二課", "三課", "四課"):
        v = sk.get(k)
        if v:
            lines.append(f"  {k}: {v[0]}  天將 {v[1]}")
    lines.append("")
    lines.append("[天地盤]  (地盤支 → 天盤支 / 天將)")
    earth_to_sky = r.get("地轉天盤", {})
    earth_to_gen = r.get("地轉天將", {})
    order = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
    lines.append("  " + "  ".join(f"{b}→{earth_to_sky.get(b,'?')}{earth_to_gen.get(b,'?')}" for b in order))
    return "\n".join(lines)


# ---- PNG 렌더 ----
_FONT_CANDIDATES = [
    "C:/Windows/Fonts/malgun.ttf",
    "C:/Windows/Fonts/batang.ttc",
    "C:/Windows/Fonts/gulim.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
]


def _font(size: int) -> ImageFont.FreeTypeFont:
    for p in _FONT_CANDIDATES:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


_SIZE = 1080
_CELL = _SIZE // 4


def render_png(r: dict) -> bytes:
    img = PILImage.new("RGB", (_SIZE, _SIZE), "white")
    d = ImageDraw.Draw(img)
    earth_to_sky = r.get("地轉天盤", {})
    earth_to_gen = r.get("地轉天將", {})

    f_gen = _font(26)
    f_sky = _font(46)
    f_earth = _font(22)
    f_small = _font(20)
    f_title = _font(34)

    # 외곽 12궁
    for branch, (row, col) in _BRANCH_CELL.items():
        x, y = col * _CELL, row * _CELL
        d.rectangle([x, y, x + _CELL, y + _CELL], outline="#c8c8c8", width=1)
        gen = earth_to_gen.get(branch, "?")
        sky = earth_to_sky.get(branch, "?")
        # 天將 (상단, 청색)
        d.text((x + 14, y + 12), gen, font=f_gen, fill="#1f6fb2")
        # 天盤支 (중앙, 큼, 적색)
        d.text((x + _CELL / 2, y + _CELL / 2), sky, font=f_sky, fill="#c0392b", anchor="mm")
        # 地盤支 (우하단 고정 위치 라벨, 회색)
        d.text((x + _CELL - 12, y + _CELL - 10), branch, font=f_earth, fill="#888888", anchor="rs")

    # 중앙 정보 패널 (2×2)
    cx0, cy0 = _CELL, _CELL
    cw, ch = _CELL * 2, _CELL * 2
    d.rectangle([cx0, cy0, cx0 + cw, cy0 + ch], fill="#fafafa", outline="#c8c8c8", width=1)
    cx = cx0 + cw / 2
    cy = cy0 + 18
    d.text((cx, cy), "大六壬 천지반", font=f_title, fill="#222222", anchor="ma"); cy += 46
    inp = r.get("_input", {})
    rows = [
        f"{inp.get('datetime') or '수동 간지'}",
        f"節氣 {r.get('節氣')} · 農曆 {r.get('農曆月')}월",
        f"{r.get('日期')}",
        f"格局 {' / '.join(r.get('格局', [])) or '-'}",
        f"日馬 {r.get('日馬', '-')}",
        "",
        "[三傳]  支 將 親",
    ]
    sp = r.get("三傳", {})
    for k in ("初傳", "中傳", "末傳"):
        v = sp.get(k)
        if v:
            rows.append(f"{k} {v[0]} {v[1]} {v[2]}")
    rows.append("")
    rows.append("[四課]")
    sk = r.get("四課", {})
    line = "  ".join(f"{k[0]}:{sk[k][0]}{sk[k][1]}" for k in ("一課", "二課", "三課", "四課") if sk.get(k))
    rows.append(line)
    for t in rows:
        d.text((cx, cy), t, font=f_small, fill="#444444", anchor="ma")
        cy += 27

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
