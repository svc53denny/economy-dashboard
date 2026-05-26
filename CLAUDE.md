# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요

실시간 경제 소식 대시보드. RSS 피드와 yfinance로 뉴스·시장 데이터를 수집하고,
OpenRouter LLM으로 뉴스를 자동 요약해 Streamlit 대시보드에 표시합니다.

## 주요 명령어

```bash
# 패키지 설치
pip install -r project/requirements.txt

# 대시보드 실행 (project/ 디렉토리 기준)
streamlit run project/dashboard/app.py

# 독립 HTML 내보내기
python project/dashboard/export_html.py

# 테스트
pytest project/tests/ -v
```

## 환경 변수

- `.env` (루트) 또는 `project/.env` 에 `OPENROUTER_API_KEY` 설정
- `python-dotenv`의 `find_dotenv()`가 상위 디렉토리까지 자동 탐색

## 아키텍처

```
project/
├── db/             # SQLite (economy.db) — schema.py 초기화, helpers.py CRUD
├── modules/        # news.py(RSS), market.py(yfinance), summarizer.py(OpenRouter)
├── scheduler/      # APScheduler 백그라운드 스레드, 10분 주기 갱신
└── dashboard/      # app.py(Streamlit), export_html.py → index.html
```

**데이터 흐름:** scheduler → modules → db → dashboard (read-only)

**스케줄러 싱글턴:** `st.session_state.initialized`로 Streamlit 재실행 시 중복 기동 방지.

**LLM 호출 제한:** 미요약 뉴스 회당 최대 5건만 처리해 과금 억제.

## PRD

`docs/PRD.md` 에 기능 요구사항, KPI, 에이전트 간 인터페이스 정의 포함.
