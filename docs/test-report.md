# 대시보드 테스트 리포트

- **테스트 일자:** 2026-06-09
- **테스트 도구:** Playwright MCP + pytest
- **대상:** `project/dashboard/app.py` (Streamlit 대시보드)

---

## pytest 단위 테스트 결과

```
10 passed in 0.87s
```

| 테스트 파일 | 테스트 | 결과 |
|------------|--------|------|
| test_db.py | test_insert_and_retrieve | ✅ |
| test_db.py | test_duplicate_url_ignored | ✅ |
| test_db.py | test_unsummarized_then_summarized | ✅ |
| test_db.py | test_market_data_upsert_and_latest | ✅ |
| test_market.py | test_returns_market_list | ✅ |
| test_market.py | test_change_pct_calculated | ✅ |
| test_market.py | test_failed_symbol_skipped | ✅ |
| test_news.py | test_returns_articles | ✅ |
| test_news.py | test_failed_feed_skipped | ✅ |
| test_news.py | test_empty_title_filtered | ✅ |

---

## Playwright E2E 테스트 결과

### 1차 테스트 — 버그 발견

| # | 항목 | 결과 | 비고 |
|---|------|------|------|
| 1 | 페이지 초기 로드 | ✅ | 헤더·사이드바·전체 섹션 렌더링 정상 |
| 2 | 시장 지표 메트릭 | ✅ | 8개 자산(KOSPI·KOSDAQ·S&P500·NASDAQ·Dow·Gold·WTI·USD/KRW) |
| 3 | Plotly 등락률 바차트 | ✅ | 8개 자산, 툴바 8개 버튼 확인 |
| 4 | **Fear & Greed Index** | ❌ | `@st.cache_data`가 None 캐시 → 경고 표시 |
| 5 | 뉴스 expander | ✅ | 원문 링크·AI 요약·수집 시간 표시 |
| 6 | AI 요약 체크박스 OFF | ✅ | 요약 숨김 정상 |
| 7 | AI 요약 체크박스 ON | ✅ | 요약 재표시 정상 |
| 8 | 뉴스 표시 수 슬라이더 | ✅ | 값 변경 시 뉴스 개수 동적 반영 |
| 9 | 새로고침 버튼 | ✅ | 타임스탬프 갱신 확인 |
| 10 | 원문 링크 | ✅ | yna.co.kr URL 유효, target="_blank" |

**발견된 버그:** `_cached_fear_greed()`에서 API 실패 시 `None`이 10분간 캐시되어 이후 API 정상화 후에도 경고가 표시됨.

**수정 내용 (`project/dashboard/app.py`):**
```python
# 수정 전
@st.cache_data(ttl=600)
def _cached_fear_greed():
    return fetch_fear_greed()

fg = _cached_fear_greed()

# 수정 후
@st.cache_data(ttl=600)
def _cached_fear_greed():
    result = fetch_fear_greed()
    if result is None:
        raise RuntimeError("Fear & Greed 데이터 없음")  # None은 캐시 안 됨
    return result

try:
    fg = _cached_fear_greed()
except Exception:
    fg = None
```

---

### 2차 테스트 — 버그 수정 후 전체 통과

| # | 항목 | 결과 | 상세 |
|---|------|------|------|
| 1 | 페이지 초기 로드 | ✅ | 헤더·사이드바·전체 섹션 렌더링 정상 |
| 2 | 시장 지표 메트릭 | ✅ | 메트릭 카드 11개 (자산 8 + F&G 추이 3) |
| 3 | Plotly 차트 2개 | ✅ | 등락률 바차트 + Fear & Greed 게이지 |
| 4 | Fear & Greed Index | ✅ | 경고 없음, score 40.1 / rating: fear |
| 5 | F&G 추이 비교 | ✅ | 전일 40.1(+0.0) / 1주 전 56.1(-16.0) / 1달 전 67.3(-27.2) |
| 6 | 뉴스 expander | ✅ | 원문 링크·AI 요약·수집 시간 표시 |
| 7 | AI 요약 체크박스 OFF | ✅ | 체크 해제 시 요약 즉시 숨김 |
| 8 | 뉴스 표시 수 슬라이더 | ✅ | 20 → 10 변경 시 뉴스 10개로 반영 |
| 9 | 새로고침 버튼 | ✅ | 13:43:19 → 13:43:39 타임스탬프 갱신 |

**최종 결과: 9/9 통과**
