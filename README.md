# mcp-liuren

점단 일시를 받아 **대육임(大六壬)** 과를 세워 三傳·四課·天地盤·格局·神煞 텍스트와
**천지반 PNG**를 반환하는 MCP 서버. (Python 런타임)

> 구조·네이밍·PNG·설치 규약은 [`STANDARD.md`](STANDARD.md)를 따른다(§6 Python 블록).

---

## 구성 / 계산

- **점단 엔진**: [`kinliuren`](https://pypi.org/project/kinliuren/) — 大六壬 과 생성.
- **달력 레이어**: [`lunar_python`](https://pypi.org/project/lunar-python/) — 일시 → (節氣, 農曆月, 日干支, 時干支) 변환.
  - ⚠️ kinliuren은 간지·절기를 **스스로 계산하지 않으므로** 이 레이어가 필수다.
  - 절기명은 kinliuren이 기대하는 **번체**로 보정한다(惊蛰→驚蟄 등).
  - 月將은 점단 시각의 **직전 절기**(`getPrevJieQi`)로 결정한다.
- **렌더**: [`Pillow`](https://pypi.org/project/pillow/) — 천지반 4×4 그리드, 한글/한자 폰트.
- 결정론적: 같은 입력 → 같은 과.

> **간지 변환 신뢰성**: 日干支 산출을 천문 JDN 공식(상수 JDN(2000-01-01)=2451545)과
> 교차검증했다. 예: 2024-02-10 = **甲辰일**, 1949-10-01 = **甲子일**(만세력 일치).

---

## 도구

### `get_liuren`

| 파라미터 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `datetime_str` | string `YYYY-MM-DD HH:MM` | ✅* | 점단 일시 |
| `manualGanzhi` | object | | (선택) 간지 직접 입력 시 달력 변환 생략 |

\* `manualGanzhi`를 주면 `datetime_str`은 생략 가능.
`manualGanzhi` 형식: `{"jieqi": "立春", "cmonth": 1, "dayGanzhi": "甲辰", "hourGanzhi": "辛未"}`

**출력 (둘 다 반환)**:
1. 구조화 텍스트 — 三傳(支·天將·六親·遁干) / 四課 / 天地盤 / 格局 / 神煞(日馬)
2. 천지반 PNG (1080×1080, 12궁 그리드 + 중앙 정보 패널)

예제 출력: [`examples/liuren_example.png`](examples/liuren_example.png) (`2024-02-10 14:30`).

---

## 설치 (Python)

```bash
git clone https://github.com/molpass/mcp-liuren.git
cd mcp-liuren
python -m venv .venv && . .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

예제 천지반을 직접 생성해 보려면:

```bash
python examples/generate-example.py   # examples/liuren_example.png 재생성
```

> **폰트**: 한자·한글 라벨을 위해 한글 가능 폰트가 필요하다.
> Windows는 Malgun Gothic 기본 탑재. Linux는 Noto CJK / Nanum 권장.

---

## MCP 등록 (서버명 `liuren`, STANDARD §6 Python)

```json
{
  "mcpServers": {
    "liuren": {
      "command": "/abs/path/mcp-liuren/.venv/bin/python",
      "args": ["/abs/path/mcp-liuren/server.py"]
    }
  }
}
```

> `/abs/path`는 실제 절대경로로 바꾼다.
> Windows 예: `"command": "C:/Users/<you>/mcp-liuren/.venv/Scripts/python.exe"`,
> `"args": ["C:/Users/<you>/mcp-liuren/server.py"]`

---

## 스킬

페어링 스킬: [`skill/liuren.skill.md`](skill/liuren.skill.md).

## License

MIT
