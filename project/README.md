# 실시간 경제 소식 대시보드

RSS 피드·yfinance로 경제 뉴스와 시장 지표를 수집하고,
OpenRouter LLM으로 뉴스를 자동 요약해 Streamlit 대시보드에 표시합니다.

---

## 실행 방법

```bash
# 1. 패키지 설치
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

## 테스트 실행

```bash
pytest tests/ -v
```

---

## 디렉토리 구조

```
project/
├── modules/        # 데이터 수집 (news, market) + LLM 요약 (summarizer)
├── db/             # SQLite 스키마 및 CRUD 헬퍼
├── scheduler/      # APScheduler 10분 주기 자동 갱신
├── dashboard/      # Streamlit 앱 + HTML 내보내기
├── tests/          # pytest 테스트 스위트
└── docs/           # 에이전트 간 핸드오프 문서
```

---

## 에이전트 역할

| 에이전트 | 담당 |
|----------|------|
| product-prd-manager | PRD 작성, 개발 조율, 최종 검토 |
| backend-architect | DB 스키마, 수집 모듈, 스케줄러 |
| llm-integration-specialist | OpenRouter 연동, 요약 모듈 |
| frontend-dev-expert | Streamlit 대시보드, HTML 내보내기 |
| qa-engineer | pytest 테스트, 버그 리포트 |
