---
name: liuren
description: Use when the user wants a Da Liu Ren (대육임/大六壬) divination reading — "대육임 점 봐줘", "육임으로 봐줘", "지금 시각으로 과 세워줘". Resolves the divination time to ganzhi, calls get_liuren, returns the heaven-earth plate PNG with a short reading.
---

# liuren

`mcp-liuren` 서버의 `get_liuren` 도구를 호출해 대육임 과(三傳·四課·天地盤·格局·神煞)와
천지반 PNG를 만든다. 도구는 "사실"(간지 변환·과 생성·렌더), 이 스킬은 "의미"(시각 확보 + 짧은 해석)를 담당한다.

## 트리거

- "대육임 점 봐줘", "육임으로 봐줘"
- "지금 시각으로 과 세워줘", "오늘 OO시에 점단"
- 특정 일시의 대육임 천지반/삼전을 보려는 요청

## 동작

1. **점단 일시**를 확보한다.
   - "지금"이면 현재 일시를 `YYYY-MM-DD HH:MM`로 만들어 넣는다.
   - 특정 일시를 말하면 그 값을 쓴다. 시각이 모호하면(분 단위) 한 번 확인한다.
   - 사용자가 간지를 직접 알고 있으면 `manualGanzhi`로 넘겨 달력 변환을 생략할 수 있다.
2. `get_liuren` 을 호출한다.
3. 반환된 **천지반 PNG**를 보여주고, 핵심을 요약한다:
   - **三傳(초·중·말전)** 의 흐름을 먼저 짚는다(일의 시작→전개→결말 상징).
   - **格局**(과의 종류)과 **日馬** 등 신살을 한두 줄로.

## 파라미터 요약

`datetime_str`("YYYY-MM-DD HH:MM"), 또는 `manualGanzhi`
(`{jieqi, cmonth, dayGanzhi, hourGanzhi}`). 둘 중 하나 필수.

## 주의

- 시각이 핵심이다 — 時干支가 바뀌면 과 전체가 달라진다. 모르면 사용자에게 확인한다.
- 子시 경계(23:00~)·절기 경계 부근은 결과가 민감하니, 가능하면 정확한 분까지 받는다.
- 대육임은 전통 점술 체계다. 해석은 재미/참고용으로 단정적이지 않게 전달한다.
