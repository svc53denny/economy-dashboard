# 📈 실시간 경제 소식 대시보드

RSS 피드·yfinance로 경제 뉴스와 시장 지표를 수집하고,
OpenRouter LLM으로 뉴스를 자동 요약해 Streamlit 대시보드에 표시합니다.

---

## 주요 기능

- **시장 지표** — KOSPI·KOSDAQ·S&P 500·NASDAQ·Dow Jones·Gold·WTI Oil·USD/KRW 실시간 가격 및 등락률 바차트
- **Fear & Greed Index** — CNN 공포/탐욕 지수 게이지 + 전일·1주 전·1달 전 추이 비교
- **최신 경제 뉴스** — 연합뉴스 등 RSS 수집, AI 요약 자동 생성 (OpenRouter · Gemma)
- **사이드바 설정** — 뉴스 표시 수 슬라이더(5~50), AI 요약 표시 토글, 수동 새로고침
- **10분 주기 자동 갱신** — APScheduler 백그라운드 스레드
- **독립 HTML 스냅샷** — 외부 의존 없이 브라우저에서 바로 열리는 `index.html` 내보내기

---

## 실행 방법

```bash
# 1. 패키지 설치 (project/ 기준)
pip install -r requirements.txt

# 2. 환경변수 설정
cp .env.example .env
# .env 파일에 OPENROUTER_API_KEY 입력

# 3. 대시보드 실행
streamlit run dashboard/app.py

# 4. (선택) 독립 HTML 내보내기
python dashboard/export_html.py
# → dashboard/index.html 생성됨
```

---

## 환경 변수

| 변수 | 설명 |
|------|------|
| `OPENROUTER_API_KEY` | OpenRouter API 키 (뉴스 AI 요약에 사용) |

`.env` 파일은 루트 또는 `project/` 디렉토리에 두면 `python-dotenv`가 자동 탐색합니다.

---

## 테스트 실행

```bash
pytest tests/ -v
```

---

## 디렉토리 구조

```
project/
├── db/             # SQLite (economy.db) — schema.py 초기화, helpers.py CRUD
├── modules/        # news.py(RSS), market.py(yfinance/CNN), summarizer.py(OpenRouter)
├── scheduler/      # APScheduler 백그라운드 스레드, 10분 주기 갱신
├── dashboard/      # app.py(Streamlit), export_html.py → index.html
├── tests/          # pytest 테스트 스위트
└── docs/           # PRD 및 에이전트 핸드오프 문서
```

**데이터 흐름:** `scheduler → modules → db → dashboard (read-only)`

---

## 에이전트 역할

| 에이전트 | 담당 |
|----------|------|
| product-prd-manager | PRD 작성, 개발 조율, 최종 검토 |
| backend-architect | DB 스키마, 수집 모듈, 스케줄러 |
| llm-integration-specialist | OpenRouter 연동, 요약 모듈 |
| frontend-dev-expert | Streamlit 대시보드, HTML 내보내기 |
| qa-engineer | pytest 테스트, 버그 리포트 |

---

## 변경 이력

| 버전 | 내용 |
|------|------|
| 초기 | 실시간 경제 소식 대시보드 최초 구현 |
| hotfix | Fear & Greed `None` 캐시 버그 수정 — 최초 API 실패 시 `@st.cache_data`가 `None`을 10분간 캐시하던 문제 해결 |
