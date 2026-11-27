"""
AI 응용 학습 (AI Native Master) - M1-1
보너스 과제: 원/달러(USD/KRW) 환율 인터랙티브 웹 대시보드
실행 명령: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import os

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="원/달러 환율 트렌드 대시보드",
    page_icon="💵",
    layout="wide"
)

# 2. 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# 3. 데이터 로드 (캐싱)
@st.cache_data
def load_data():
    file_path = "data/usdkrw_2023_2024.csv"
    if not os.path.exists(file_path):
        df = yf.download("KRW=X", start="2023-01-01", end="2024-12-31")
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        os.makedirs("data", exist_ok=True)
        df.to_csv(file_path, encoding="utf-8-sig")
    else:
        df = pd.read_csv(file_path, index_col=0, parse_dates=True)
    return df

df = load_data()

# 4. 헤더
st.title("💵 원/달러(USD/KRW) 환율 트렌드 & 거시경제 충격 대시보드")
st.caption("AI 응용 학습 (AI Native Master) M1-1 보너스 산출물 | Yahoo Finance KRW=X 일봉 데이터 기반")

# 5. 사이드바 컨트롤러 (URL 쿼리 파라미터를 통한 시나리오 직접 진입 지원)
st.sidebar.header("🔍 분석 조건 및 필터")

min_date = df.index.min().date()
max_date = df.index.max().date()

qp = st.query_params
try:
    default_start = pd.to_datetime(qp["start"]).date() if "start" in qp else min_date
    default_end = pd.to_datetime(qp["end"]).date() if "end" in qp else max_date
    default_start = max(min_date, min(default_start, max_date))
    default_end = max(default_start, min(default_end, max_date))
except Exception:
    default_start, default_end = min_date, max_date

try:
    default_short = int(qp["short"]) if "short" in qp else 20
    default_short = max(5, min(default_short, 30))
except Exception:
    default_short = 20

try:
    default_long = int(qp["long"]) if "long" in qp else 60
    default_long = max(30, min(default_long, 120))
except Exception:
    default_long = 60

selected_dates = st.sidebar.date_input(
    "조회 기간 설정",
    value=[default_start, default_end],
    min_value=min_date,
    max_value=max_date
)

sma_short_val = st.sidebar.slider("단기 이동평균선(일수)", min_value=5, max_value=30, value=default_short, step=5)
sma_long_val = st.sidebar.slider("중기 이동평균선(일수)", min_value=30, max_value=120, value=default_long, step=10)

show_shocks = st.sidebar.checkbox("거시 충격일(|등락률| >= 1.5%) 강조 표시", value=True)
show_thresholds = st.sidebar.checkbox("1,300원 / 1,400원 마디선 표시", value=True)

# 6. 데이터 필터링
if isinstance(selected_dates, (list, tuple)) and len(selected_dates) == 2:
    start_dt, end_dt = pd.to_datetime(selected_dates[0]), pd.to_datetime(selected_dates[1])
    sub_df = df.loc[start_dt:end_dt].copy()
else:
    sub_df = df.copy()

if sub_df.empty:
    st.error("선택한 기간에 데이터가 없습니다.")
    st.stop()

# 파생변수 계산
sub_df['SMA_Short'] = sub_df['Close'].rolling(window=sma_short_val).mean()
sub_df['SMA_Long'] = sub_df['Close'].rolling(window=sma_long_val).mean()
sub_df['Daily_Return'] = sub_df['Close'].pct_change() * 100

# 7. KPI 메트릭 카드
st.subheader("📌 환율 핵심 성과 지표 (KPIs)")
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

start_close = sub_df['Close'].iloc[0]
end_close = sub_df['Close'].iloc[-1]
ret = ((end_close - start_close) / start_close) * 100
highest_price = sub_df['High'].max()
lowest_price = sub_df['Low'].min()

kpi1.metric("조회 시작일 환율", f"{start_close:,.1f} 원")
kpi2.metric("조회 종료일 환율", f"{end_close:,.1f} 원", f"{ret:+.2f}%")
kpi3.metric("기간 최고 환율", f"{highest_price:,.1f} 원")
kpi4.metric("기간 최저 환율", f"{lowest_price:,.1f} 원")

st.divider()

# 8. 메인 차트
st.subheader(f"📊 환율 추세 및 이동평균선 ({sma_short_val}일 vs {sma_long_val}일)")

fig, (ax_price, ax_ret) = plt.subplots(2, 1, figsize=(14, 8), sharex=True, gridspec_kw={'height_ratios': [3, 1.2]})

# 환율 및 이평선 차트
ax_price.plot(sub_df.index, sub_df['Close'], label='환율 종가 (KRW/USD)', color='#333333', linewidth=1.5, alpha=0.7)
ax_price.plot(sub_df.index, sub_df['SMA_Short'], label=f'단기선({sma_short_val}일)', color='#ff7f0e', linewidth=2.0)
ax_price.plot(sub_df.index, sub_df['SMA_Long'], label=f'중기선({sma_long_val}일)', color='#2ca02c', linewidth=2.0)

ax_price.fill_between(sub_df.index, sub_df['SMA_Short'], sub_df['SMA_Long'],
                      where=(sub_df['SMA_Short'] >= sub_df['SMA_Long']), color='orange', alpha=0.15, label='환율 상승 국면')
ax_price.fill_between(sub_df.index, sub_df['SMA_Short'], sub_df['SMA_Long'],
                      where=(sub_df['SMA_Short'] < sub_df['SMA_Long']), color='blue', alpha=0.1, label='환율 하락 국면')

if show_thresholds:
    ax_price.axhline(1300, color='#ff7f0e', linestyle='--', linewidth=1.0, alpha=0.7, label='1,300원선')
    ax_price.axhline(1400, color='#d62728', linestyle=':', linewidth=1.2, alpha=0.8, label='1,400원선')

ax_price.set_ylabel("환율 (원/달러)", fontsize=11)
ax_price.legend(loc='upper left')
ax_price.grid(True, linestyle='--', alpha=0.5)

# 일일 등락률 보조 차트
colors = ['#d62728' if abs(x) >= 1.5 and show_shocks else '#1f77b4' for x in sub_df['Daily_Return'].fillna(0)]
ax_ret.bar(sub_df.index, sub_df['Daily_Return'], color=colors, width=1.0)
ax_ret.axhline(0, color='black', linewidth=0.8)
if show_shocks:
    ax_ret.axhline(1.5, color='red', linestyle=':', linewidth=0.8)
    ax_ret.axhline(-1.5, color='red', linestyle=':', linewidth=0.8)
ax_ret.set_ylabel("일일 등락률 (%)", fontsize=11)
ax_ret.grid(True, linestyle='--', alpha=0.5)

st.pyplot(fig)

# 9. 시나리오 가이드
with st.expander("💡 대시보드 추천 탐색 시나리오 (클릭하여 열기)"):
    st.markdown(r"""
    * **시나리오 1: 1,400원 돌파 및 연말 초고환율 구간 집중 탐색**
      * 사이드바 날짜를 `2024-10-01 ~ 2024-12-30`으로 설정하여, 1,315.3원(10/1)에서 1,472.8원(12/30)까지 단 3개월 만에 +11.97% 급등(장중 최고 1,487.0원)하는 구간을 관찰하세요.
    * **시나리오 2: 이동평균선 민감도(10일/30일) 및 거시 충격일 탐색**
      * 단기선을 `10일`, 중기선을 `30일`로 조절해 골든크로스 신호 민감도를 비교하고, 빨간색으로 표시된 일일 등락률 $\pm 1.5\%$ 초과일을 FOMC·미 대선·비상계엄 등 거시 이벤트와 연결해 보세요.
    """)

# 10. 데이터 테이블
with st.expander("🔍 최근 환율 상세 데이터 테이블"):
    st.dataframe(sub_df[['Open', 'High', 'Low', 'Close', 'SMA_Short', 'SMA_Long', 'Daily_Return']].tail(15))
