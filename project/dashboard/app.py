import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

from db.schema import init_db
from db.helpers import get_recent_news, get_latest_market_data
from scheduler.jobs import start_scheduler
from modules.market import fetch_fear_greed


@st.cache_data(ttl=600)
def _cached_fear_greed():
    result = fetch_fear_greed()
    if result is None:
        raise RuntimeError("Fear & Greed 데이터 없음")
    return result

st.set_page_config(
    page_title="실시간 경제 소식 대시보드",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "initialized" not in st.session_state:
    init_db()
    start_scheduler()
    st.session_state.initialized = True

# ── 사이드바 ──────────────────────────────────────────────
with st.sidebar:
    st.title("⚙️ 설정")
    if st.button("🔄 지금 새로고침"):
        st.rerun()
    st.caption(f"마지막 로드: {datetime.now().strftime('%H:%M:%S')}")
    st.markdown("---")
    news_limit   = st.slider("뉴스 표시 수", min_value=5, max_value=50, value=20)
    show_summary = st.checkbox("AI 요약 표시", value=True)
    st.markdown("---")
    st.caption("데이터 자동 갱신: 10분 주기")

# ── 헤더 ──────────────────────────────────────────────────
st.title("📈 실시간 경제 소식 대시보드")
st.markdown("---")

# ── 시장 지표 섹션 ─────────────────────────────────────────
st.subheader("🌐 시장 지표")
market_data = get_latest_market_data()

if market_data:
    cols = st.columns(min(len(market_data), 4))
    for i, item in enumerate(market_data):
        arrow = "▲" if item["change_pct"] >= 0 else "▼"
        color = "🟢" if item["change_pct"] >= 0 else "🔴"
        cols[i % 4].metric(
            label=f"{color} {item['name']}",
            value=f"{item['price']:,.2f}",
            delta=f"{arrow} {item['change_pct']:+.2f}%",
        )

    df = pd.DataFrame(market_data)
    bar_colors = ["#26a69a" if v >= 0 else "#ef5350" for v in df["change_pct"]]
    fig = go.Figure(go.Bar(
        x=df["name"],
        y=df["change_pct"],
        marker_color=bar_colors,
        text=[f"{v:+.2f}%" for v in df["change_pct"]],
        textposition="outside",
    ))
    fig.update_layout(
        title="등락률 (%)",
        yaxis_title="%",
        height=320,
        showlegend=False,
        margin=dict(t=40, b=20, l=20, r=20),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("⏳ 시장 데이터를 수집 중입니다. 잠시 후 새로고침해 주세요.")

st.markdown("---")

# ── Fear & Greed 섹션 ─────────────────────────────────────
st.subheader("😱 CNN Fear & Greed Index")
try:
    fg = _cached_fear_greed()
except Exception:
    fg = None

if fg:
    score = fg["score"]

    # 점수에 따른 색상
    if score <= 25:
        bar_color, label_ko = "#ef5350", "극단적 공포"
    elif score <= 45:
        bar_color, label_ko = "#ff9800", "공포"
    elif score <= 55:
        bar_color, label_ko = "#ffeb3b", "중립"
    elif score <= 75:
        bar_color, label_ko = "#66bb6a", "탐욕"
    else:
        bar_color, label_ko = "#26a69a", "극단적 탐욕"

    gauge_fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        delta={"reference": fg["prev_close"], "valueformat": ".1f"},
        title={"text": f"{fg['rating']} ({label_ko})", "font": {"size": 18}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1},
            "bar":  {"color": bar_color},
            "steps": [
                {"range": [0,  25], "color": "#4a1010"},
                {"range": [25, 45], "color": "#4a2c10"},
                {"range": [45, 55], "color": "#3a3a10"},
                {"range": [55, 75], "color": "#1a3a1a"},
                {"range": [75, 100], "color": "#0d2e2e"},
            ],
            "threshold": {
                "line": {"color": "white", "width": 3},
                "thickness": 0.8,
                "value": score,
            },
        },
        number={"font": {"size": 48}},
    ))
    gauge_fig.update_layout(
        height=300,
        margin=dict(t=40, b=10, l=30, r=30),
        paper_bgcolor="rgba(0,0,0,0)",
        font={"color": "#e0e0e0"},
    )

    col_gauge, col_hist = st.columns([2, 1])
    with col_gauge:
        st.plotly_chart(gauge_fig, use_container_width=True)
    with col_hist:
        st.markdown("**추이 비교**")
        st.metric("전일",  fg["prev_close"],   delta=f"{score - fg['prev_close']:+.1f}")
        st.metric("1주 전", fg["prev_1_week"],  delta=f"{score - fg['prev_1_week']:+.1f}")
        st.metric("1달 전", fg["prev_1_month"], delta=f"{score - fg['prev_1_month']:+.1f}")
else:
    st.warning("Fear & Greed 데이터를 불러올 수 없습니다.")

st.markdown("---")

# ── 뉴스 섹션 ─────────────────────────────────────────────
st.subheader("📰 최신 경제 뉴스")
news = get_recent_news(limit=news_limit)

if news:
    for item in news:
        header = f"**[{item['source']}]** {item['title']}"
        with st.expander(header):
            st.markdown(f"🔗 [기사 원문 보기]({item['url']})")
            if show_summary:
                if item.get("summary"):
                    st.info(f"**AI 요약:** {item['summary']}")
                else:
                    st.caption("⏳ AI 요약 생성 중...")
            st.caption(f"수집: {item['fetched_at']}")
else:
    st.info("⏳ 뉴스를 수집 중입니다. 잠시 후 새로고침해 주세요.")

# ── 푸터 ──────────────────────────────────────────────────
st.markdown("---")
st.caption("Powered by OpenRouter · yfinance · Streamlit")
