"""
현재 DB 데이터를 읽어 독립 실행 가능한 index.html을 생성합니다.
실행: python dashboard/export_html.py
"""
import sys
import os
import json
import math
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.schema import init_db
from db.helpers import get_latest_market_data, get_recent_news
from modules.market import fetch_fear_greed

# ── 데이터 수집 ───────────────────────────────────────────────────
init_db()
market       = get_latest_market_data()
news         = get_recent_news(limit=30)
fg           = fetch_fear_greed()
generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

market_json = json.dumps(market, ensure_ascii=False)
news_json   = json.dumps(news,   ensure_ascii=False)

# ── Fear & Greed SVG 게이지 ───────────────────────────────────────
CX, CY, R_OUT, R_IN = 100, 100, 82, 54

ZONES = [
    (180, 135, "#b71c1c", "극단적 공포"),
    (135,  99, "#e65100", "공포"),
    ( 99,  81, "#f57f17", "중립"),
    ( 81,  45, "#33691e", "탐욕"),
    ( 45,   0, "#004d40", "극단적 탐욕"),
]


def polar_xy(r, deg):
    rad = math.radians(deg)
    return CX + r * math.cos(rad), CY - r * math.sin(rad)


def arc_sector(r_out, r_in, a1, a2, color):
    ox1, oy1 = polar_xy(r_out, a1)
    ox2, oy2 = polar_xy(r_out, a2)
    ix1, iy1 = polar_xy(r_in,  a1)
    ix2, iy2 = polar_xy(r_in,  a2)
    large = 1 if abs(a1 - a2) > 180 else 0
    d = (f"M {ox1:.2f},{oy1:.2f} "
         f"A {r_out},{r_out} 0 {large},1 {ox2:.2f},{oy2:.2f} "
         f"L {ix2:.2f},{iy2:.2f} "
         f"A {r_in},{r_in} 0 {large},0 {ix1:.2f},{iy1:.2f} Z")
    return f'<path d="{d}" fill="{color}"/>'


gauge_arcs = "\n  ".join(arc_sector(R_OUT, R_IN, a1, a2, c) for a1, a2, c, _ in ZONES)

if fg:
    score        = fg["score"]
    needle_angle = 180 - score * 1.8
    nx, ny       = polar_xy(74, needle_angle)

    if score <= 25:   needle_color, label_ko = "#ef5350", "극단적 공포"
    elif score <= 45: needle_color, label_ko = "#ff9800", "공포"
    elif score <= 55: needle_color, label_ko = "#ffeb3b", "중립"
    elif score <= 75: needle_color, label_ko = "#66bb6a", "탐욕"
    else:             needle_color, label_ko = "#26a69a", "극단적 탐욕"

    def _delta(v):
        d = score - v
        c = "#26a69a" if d >= 0 else "#ef5350"
        a = "▲" if d >= 0 else "▼"
        return f'{v:.1f} <span style="color:{c}">{a}{abs(d):.1f}</span>'

    needle_svg = f"""
  <line x1="{CX}" y1="{CY}" x2="{nx:.2f}" y2="{ny:.2f}"
        stroke="{needle_color}" stroke-width="3.5" stroke-linecap="round"/>
  <circle cx="{CX}" cy="{CY}" r="5.5" fill="{needle_color}"/>
  <text x="{CX}" y="86" text-anchor="middle" fill="white"
        font-size="20" font-weight="bold" font-family="Segoe UI,sans-serif">{score:.1f}</text>
  <text x="{CX}" y="100" text-anchor="middle" fill="#aaa"
        font-size="8.5" font-family="Segoe UI,sans-serif">{fg['rating'].upper()} · {label_ko}</text>"""

    fg_stats_html = f"""
    <div class="fg-stats">
      <div class="fg-stat"><span class="fg-label">전일</span>{_delta(fg['prev_close'])}</div>
      <div class="fg-stat"><span class="fg-label">1주 전</span>{_delta(fg['prev_1_week'])}</div>
      <div class="fg-stat"><span class="fg-label">1달 전</span>{_delta(fg['prev_1_month'])}</div>
    </div>"""
else:
    needle_svg = '<text x="100" y="90" text-anchor="middle" fill="#888" font-size="10">데이터 없음</text>'
    fg_stats_html = ""

fg_section = f"""
  <h2>😱 CNN Fear &amp; Greed Index</h2>
  <div class="fg-wrap">
    <svg viewBox="0 0 200 110" width="280" xmlns="http://www.w3.org/2000/svg">
      {gauge_arcs}
      {needle_svg}
    </svg>
    {fg_stats_html}
  </div>"""

# ── HTML 템플릿 ───────────────────────────────────────────────────
HTML = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>실시간 경제 소식 대시보드</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: 'Segoe UI', sans-serif; background: #0e1117; color: #e0e0e0; padding: 24px; max-width: 1100px; margin: auto; }}
    h1 {{ font-size: 1.6rem; margin-bottom: 6px; color: #fff; }}
    .subtitle {{ font-size: 0.83rem; color: #888; margin-bottom: 28px; }}
    h2 {{ font-size: 1.1rem; margin-bottom: 14px; color: #fff; }}
    .section {{ background: #1e2130; border-radius: 12px; padding: 20px; margin-bottom: 24px; }}
    /* 시장 지표 */
    .metrics {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 10px; margin-bottom: 20px; }}
    .card {{ background: #13161e; border-radius: 8px; padding: 14px; text-align: center; }}
    .card .name  {{ font-size: 0.78rem; color: #aaa; margin-bottom: 4px; }}
    .card .price {{ font-size: 1.1rem; font-weight: bold; }}
    .card .up    {{ color: #26a69a; font-size: 0.82rem; }}
    .card .down  {{ color: #ef5350; font-size: 0.82rem; }}
    /* Fear & Greed */
    .fg-wrap  {{ display: flex; align-items: center; gap: 32px; flex-wrap: wrap; }}
    .fg-stats {{ display: flex; flex-direction: column; gap: 12px; }}
    .fg-stat  {{ font-size: 0.9rem; }}
    .fg-label {{ color: #888; margin-right: 8px; font-size: 0.8rem; }}
    /* 뉴스 */
    .news-item {{ background: #13161e; border-radius: 8px; padding: 12px 16px; margin-bottom: 8px; }}
    .news-item .source {{ font-size: 0.75rem; color: #888; margin-bottom: 3px; }}
    .news-item .title  {{ font-size: 0.93rem; margin-bottom: 5px; }}
    .news-item a {{ color: #82aaff; text-decoration: none; }}
    .news-item a:hover {{ text-decoration: underline; }}
    .news-item .summary {{ font-size: 0.83rem; color: #b0b8c8; background: #0e1117;
                           border-radius: 6px; padding: 8px 12px; margin-top: 5px; }}
    footer {{ text-align: center; color: #555; font-size: 0.78rem; margin-top: 24px; }}
  </style>
</head>
<body>
  <h1>📈 실시간 경제 소식 대시보드</h1>
  <p class="subtitle">생성: {generated_at} &nbsp;|&nbsp; Powered by OpenRouter · yfinance · CNN F&amp;G</p>

  <div class="section">
    <h2>🌐 시장 지표</h2>
    <div class="metrics" id="metrics"></div>
    <canvas id="barChart" height="80"></canvas>
  </div>

  <div class="section">
    {fg_section}
  </div>

  <div class="section">
    <h2>📰 최신 경제 뉴스</h2>
    <div id="newsList"></div>
  </div>

  <footer>export_html.py 로 자동 생성된 스냅샷입니다.</footer>

  <script>
    const market = {market_json};
    const news   = {news_json};

    // 시장 카드
    const metricsEl = document.getElementById('metrics');
    market.forEach(d => {{
      const up = d.change_pct >= 0;
      metricsEl.innerHTML += `
        <div class="card">
          <div class="name">${{d.name}}</div>
          <div class="price">${{d.price.toLocaleString()}}</div>
          <div class="${{up ? 'up' : 'down'}}">${{up ? '▲' : '▼'}} ${{Math.abs(d.change_pct).toFixed(2)}}%</div>
        </div>`;
    }});

    // 바 차트
    new Chart(document.getElementById('barChart'), {{
      type: 'bar',
      data: {{
        labels: market.map(d => d.name),
        datasets: [{{
          data: market.map(d => d.change_pct),
          backgroundColor: market.map(d => d.change_pct >= 0 ? '#26a69a' : '#ef5350'),
        }}],
      }},
      options: {{
        plugins: {{ legend: {{ display: false }} }},
        scales: {{
          x: {{ ticks: {{ color: '#aaa' }}, grid: {{ display: false }} }},
          y: {{ ticks: {{ color: '#aaa' }}, grid: {{ color: '#2a2f45' }} }},
        }},
      }},
    }});

    // 뉴스
    const newsEl = document.getElementById('newsList');
    news.forEach(n => {{
      newsEl.innerHTML += `
        <div class="news-item">
          <div class="source">${{n.source}} · ${{n.fetched_at}}</div>
          <div class="title"><a href="${{n.url}}" target="_blank">${{n.title}}</a></div>
          ${{n.summary ? `<div class="summary">💡 ${{n.summary}}</div>` : ''}}
        </div>`;
    }});
  </script>
</body>
</html>"""

out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(HTML)

print(f"index.html generated: {out_path}")
