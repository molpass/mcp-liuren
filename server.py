#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""mcp-liuren — 대육임(大六壬) MCP 서버 (stdio).

get_liuren: 점단 일시(또는 수동 간지) → 三傳·四課·天地盤·格局·神煞 텍스트 + 천지반 PNG.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from mcp.server.fastmcp import FastMCP, Image

from liuren_core import divine, format_text, render_png

mcp = FastMCP("liuren")


@mcp.tool()
def get_liuren(datetime_str: str = "", manualGanzhi: Optional[dict] = None) -> list:
    """대육임 점단을 수행한다.

    Args:
        datetime_str: 점단 일시 "YYYY-MM-DD HH:MM". 수동 간지를 주면 생략 가능.
        manualGanzhi: (선택) 간지 직접 입력 시 달력 변환을 생략한다.
            형식: {"jieqi": "立春", "cmonth": 1, "dayGanzhi": "甲辰", "hourGanzhi": "辛未"}

    Returns:
        구조화 텍스트(三傳·四課·天地盤·格局·神煞)와 천지반 PNG.
    """
    dt: Optional[datetime] = None
    if not manualGanzhi:
        if not datetime_str.strip():
            raise ValueError("datetime_str('YYYY-MM-DD HH:MM') 또는 manualGanzhi가 필요합니다.")
        try:
            dt = datetime.strptime(datetime_str.strip(), "%Y-%m-%d %H:%M")
        except ValueError:
            raise ValueError(f"일시 형식 오류 (YYYY-MM-DD HH:MM): {datetime_str}")

    result = divine(dt, manualGanzhi)
    text = format_text(result)
    png = render_png(result)
    return [text, Image(data=png, format="png")]


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
