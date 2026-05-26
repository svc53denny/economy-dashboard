# PRD — 실시간 경제 소식 대시보드

## 1. 제품 목표 및 성공 지표 (KPI)

| 지표 | 목표값 |
|------|--------|
| 페이지 초기 로드 | ≤ 3초 |
| 시장 데이터 갱신 주기 | ≤ 10분 |
| AI 뉴스 요약 생성 | ≤ 30초/건 |
| 뉴스 수집 소스 | 4개 이상 RSS 피드 |
| 시장 지표 커버리지 | KOSPI·KOSDAQ·S&P·NASDAQ·USD/KRW·금·원유 |

---

## 2. 사용자 페르소나

| 페르소나 | 설명 | 핵심 니즈 |
|----------|------|-----------|
| 개인 투자자 | 30~50대, 주식·ETF 보유 | 실시간 등락률 + 관련 뉴스 요약 |
| 직장인 | 출퇴근 중 경제 뉴스 확인 | 빠른 AI 요약, 모바일 친화적 UI |
| 금융 전공 학생 | 리서치·과제 목적 | 차트, 데이터 내보내기 |

---

## 3. 기능 요구사항

### Must-have
- RSS 다중 피드 수집 (연합뉴스 경제, 한국경제, Reuters, CNN Money)
- APScheduler 기반 10분 주기 자동 갱신
- SQLite 영속 저장 (뉴스, 시장 데이터)
- yfinance 기반 시장 지표 7종 표시
- OpenRouter LLM 뉴스 요약 (gpt-4o-mini 기본)
- Streamlit 대시보드 (등락률 바 차트 + 뉴스 피드)
- 독립 실행 index.html 내보내기

### Nice-to-have
- 감성 분석 (긍정/부정/중립)
- 키워드 필터 검색
- 포트폴리오 등록 및 손익 추적
- 이메일 알림

---

## 4. 개발 단계 및 에이전트 담당

| 순서 | 에이전트 | 담당 범위 |
|------|----------|-----------|
| 1 | backend-architect | DB 스키마, 수집 모듈 (news/market), 스케줄러 |
| 2 | llm-integration-specialist | summarizer 모듈, OpenRouter 연동 |
| 3 | frontend-dev-expert | Streamlit 대시보드, export_html.py |
| 4 | qa-engineer | pytest 테스트 스위트, 버그 리포트 |
| 5 | product-prd-manager | 최종 검토, README 업데이트, DONE.md 작성 |

---

## 5. 파일 및 디렉토리 구조

```
project/
├── modules/
│   ├── __init__.py
│   ├── news.py          # RSS 수집
│   ├── market.py        # yfinance 시장 데이터
│   └── summarizer.py    # OpenRouter LLM 요약
├── db/
│   ├── __init__.py
│   ├── schema.py        # SQLite 초기화 / 경로
│   └── helpers.py       # CRUD 헬퍼 함수
├── scheduler/
│   ├── __init__.py
│   └── jobs.py          # APScheduler 작업 정의
├── dashboard/
│   ├── app.py           # Streamlit 메인 앱
│   ├── export_html.py   # index.html 생성 스크립트
│   └── index.html       # 독립 실행 HTML (자동 생성)
├── tests/
│   ├── __init__.py
│   ├── test_db.py
│   ├── test_news.py
│   └── test_market.py
├── docs/                # 에이전트 간 핸드오프 문서
├── logs/
├── requirements.txt
├── .env.example
└── README.md
```

---

## 6. 에이전트 간 인터페이스 정의

### db/helpers.py 제공 함수

| 함수 | 인자 | 반환 | 호출자 |
|------|------|------|--------|
| `init_db()` | - | None | scheduler, app.py |
| `insert_news(title, url, source, published_at)` | str×4 | None | scheduler |
| `update_news_summary(url, summary)` | str×2 | None | llm-specialist |
| `get_recent_news(limit)` | int | list[dict] | dashboard |
| `get_unsummarized_news(limit)` | int | list[dict] | llm-specialist |
| `upsert_market_data(symbol, name, price, change_pct, volume)` | mixed | None | scheduler |
| `get_latest_market_data()` | - | list[dict] | dashboard |

### modules/summarizer.py 제공 함수

| 함수 | 인자 | 반환 |
|------|------|------|
| `summarize(title, model)` | str, str | str \| None |

---

## 7. 리스크 및 의존성

| 리스크 | 영향 | 완화 방안 |
|--------|------|-----------|
| RSS 피드 URL 변경/차단 | 뉴스 미수집 | 피드별 try/except, 대체 URL 목록 유지 |
| yfinance API 제한 | 시장 데이터 누락 | fast_info 사용, 장 마감 시 캐시 활용 |
| OpenRouter 과금 | 비용 초과 | 미요약 뉴스 회당 5건 제한, 저가 모델 기본값 |
| Streamlit 재실행 중 스케줄러 중복 | 메모리 누수 | session_state로 단일 인스턴스 보장 |
| Windows 한글 경로 | 인코딩 오류 | UTF-8 명시, 경로 검증 |
