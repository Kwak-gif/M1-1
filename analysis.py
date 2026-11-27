"""
AI 응용 학습 (AI Native Master) - M1-1
원/달러(USD/KRW) 환율 트렌드 및 거시경제 충격 분석 스크립트
티커: KRW=X (Yahoo Finance) | 기간: 2023-01-01 ~ 2024-12-31
"""

import os
import sys
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.tsa.seasonal import seasonal_decompose

# Windows 콘솔 utf-8 출력 설정
if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def setup_environment():
    """폴더 생성 및 시각화 환경을 세팅합니다."""
    os.makedirs("data", exist_ok=True)
    os.makedirs("images", exist_ok=True)
    
    plt.rcParams['font.family'] = 'Malgun Gothic'
    plt.rcParams['axes.unicode_minus'] = False
    sns.set_theme(style="whitegrid", font='Malgun Gothic')
    plt.rcParams['axes.unicode_minus'] = False

def fetch_and_clean_data(ticker="KRW=X", start="2023-01-01", end="2024-12-31"):
    """Yahoo Finance에서 원/달러 환율 데이터를 수집하고 결측치를 정제합니다."""
    print(f"[1/4] 환율 데이터 수집 시작: {ticker} ({start} ~ {end})")
    df = yf.download(ticker, start=start, end=end)
    
    # yfinance 다중 인덱스 컬럼 처리
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
        
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    
    # 결측치 확인 및 ffill 보정
    missing = df.isnull().sum()
    if missing.sum() > 0:
        print(f"결측치 감지됨: {missing.to_dict()} -> ffill/bfill 적용")
        df = df.ffill().bfill()
    else:
        print("결측치 검사 완료: 결측치 0건 (완전 데이터)")
        
    # 원본 CSV 저장
    df.to_csv("data/usdkrw_2023_2024.csv", encoding="utf-8-sig")
    print(f"데이터 수집 완료: 총 {len(df)}개 거래일 데이터 확보")
    return df

def feature_engineering(df):
    """이동평균, 일일 등락률, 변동성, 거시 충격 이상치 플래그를 생성합니다."""
    print("[2/4] 시계열 파생변수 생성 및 이상치 탐색 중...")
    
    # 20일(1개월) / 60일(1분기) 단순이동평균(SMA)
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_60'] = df['Close'].rolling(window=60).mean()
    
    # 일일 환율 등락률(%)
    df['Daily_Return'] = df['Close'].pct_change() * 100
    
    # 20거래일 롤링 변동성(표준편차)
    df['Volatility_20'] = df['Daily_Return'].rolling(window=20).std()
    
    # 월별 그룹핑을 위한 연월 컬럼
    df['Year_Month'] = df.index.to_period('M')
    
    # 이상치 탐지: 일일 등락률 절댓값이 1.5% 이상인 외생 충격일 플래깅
    df['Shock_Flag'] = df['Daily_Return'].abs() >= 1.5
    shock_count = df['Shock_Flag'].sum()
    print(f"시장 거시 충격 이상치(|등락률| >= 1.5%): 총 {shock_count}일 식별됨 (삭제하지 않고 보존)")
    
    df.to_csv("data/usdkrw_processed.csv", encoding="utf-8-sig")
    return df

def generate_visualizations(df):
    """5종 고해상도 시각화 차트를 생성하여 images/ 폴더에 저장합니다."""
    print("[3/4] 시각화 이미지 5종 생성 중...")
    
    # -------------------------------------------------------------
    # 1. 2개년 환율 장기 트렌드 및 심리적 마디 가격 (1,300원, 1,400원)
    # -------------------------------------------------------------
    plt.figure(figsize=(14, 6))
    plt.plot(df.index, df['Close'], label='원/달러 환율 (KRW/USD)', color='#004ea2', linewidth=2)
    
    max_p = df['Close'].max()
    max_d = df['Close'].idxmax()
    min_p = df['Close'].min()
    min_d = df['Close'].idxmin()
    
    plt.scatter([max_d], [max_p], color='red', s=100, zorder=5, label=f'최고 환율: {max_p:,.1f}원 ({max_d.strftime("%Y-%m-%d")})')
    plt.scatter([min_d], [min_p], color='blue', s=100, zorder=5, label=f'최저 환율: {min_p:,.1f}원 ({min_d.strftime("%Y-%m-%d")})')
    
    # 1,300원 및 1,400원 마디선 표시
    plt.axhline(1300, color='#ff7f0e', linestyle='--', linewidth=1.2, label='1,300원 지지/저항선')
    plt.axhline(1400, color='#d62728', linestyle=':', linewidth=1.5, label='1,400원 심리적 위험선')
    
    plt.title("2023 ~ 2024 원/달러(USD/KRW) 환율 장기 트렌드 및 고환율 추세", fontsize=15, fontweight='bold', pad=12)
    plt.xlabel("거래일", fontsize=12)
    plt.ylabel("환율 (원/달러)", fontsize=12)
    plt.legend(loc='upper left', frameon=True)
    plt.tight_layout()
    plt.savefig("images/01_exchange_rate_trend.png", dpi=300)
    plt.close()
    
    # -------------------------------------------------------------
    # 2. 이동평균선(SMA 20/60) 수급 골든·데드크로스 분석
    # -------------------------------------------------------------
    plt.figure(figsize=(14, 6))
    plt.plot(df.index, df['Close'], label='일별 종가', color='#a0a0a0', alpha=0.5, linewidth=1.2)
    plt.plot(df.index, df['SMA_20'], label='20일 이평선(단기)', color='#e6550d', linewidth=2.0)
    plt.plot(df.index, df['SMA_60'], label='60일 이평선(중기)', color='#31a354', linewidth=2.0)
    
    plt.fill_between(df.index, df['SMA_20'], df['SMA_60'], 
                     where=(df['SMA_20'] >= df['SMA_60']), color='orange', alpha=0.15, label='환율 상승(원화 약세) 국면')
    plt.fill_between(df.index, df['SMA_20'], df['SMA_60'], 
                     where=(df['SMA_20'] < df['SMA_60']), color='blue', alpha=0.1, label='환율 하락(원화 강세) 국면')
                     
    plt.title("원/달러 환율 20일 / 60일 이동평균선(SMA) 골든·데드크로스 추세 분석", fontsize=15, fontweight='bold', pad=12)
    plt.xlabel("거래일", fontsize=12)
    plt.ylabel("환율 (원/달러)", fontsize=12)
    plt.legend(loc='upper left', frameon=True)
    plt.tight_layout()
    plt.savefig("images/02_moving_average.png", dpi=300)
    plt.close()
    
    # -------------------------------------------------------------
    # 3. 24개월 월별 롤링 변동성(표준편차) 바 차트
    # -------------------------------------------------------------
    monthly_vol = df.groupby(df['Year_Month'])['Volatility_20'].mean().dropna()
    plt.figure(figsize=(14, 6))
    bars = plt.bar([str(ym) for ym in monthly_vol.index], monthly_vol.values, color='#3182bd', width=0.65)
    plt.axhline(monthly_vol.mean(), color='red', linestyle='--', label=f'2개년 평균 변동성 ({monthly_vol.mean():.2f}%)')
    
    for bar in bars:
        h = bar.get_height()
        plt.annotate(f"{h:.2f}%",
                     xy=(bar.get_x() + bar.get_width() / 2, h),
                     xytext=(0, 3),
                     textcoords="offset points",
                     ha='center', va='bottom', fontsize=9, fontweight='bold')
                     
    plt.title("2023 ~ 2024 원/달러 환율 월별 평균 변동성(20일 표준편차)", fontsize=15, fontweight='bold', pad=12)
    plt.xlabel("연도-월 (Year-Month)", fontsize=12)
    plt.ylabel("평균 롤링 변동성 (%)", fontsize=12)
    plt.xticks(rotation=45)
    plt.legend(loc='upper right')
    plt.tight_layout()
    plt.savefig("images/03_monthly_volatility.png", dpi=300)
    plt.close()
    
    # -------------------------------------------------------------
    # 4. [보너스 A] 시계열 가법 분해 (Seasonal Decomposition)
    # -------------------------------------------------------------
    close_series = df['Close'].dropna()
    decomp = seasonal_decompose(close_series, model='additive', period=20)
    
    fig, axes = plt.subplots(4, 1, figsize=(14, 10), sharex=True)
    axes[0].plot(decomp.observed, color='#333333', label='Observed (원본 환율)')
    axes[0].set_title("원/달러 환율 시계열 4대 구성요소 분해 (Observed = Trend + Seasonal + Residual)", fontsize=14, fontweight='bold')
    axes[0].legend(loc='upper left')
    
    axes[1].plot(decomp.trend, color='#004ea2', label='Trend (장기 상승 추세선)')
    axes[1].legend(loc='upper left')
    
    axes[2].plot(decomp.seasonal, color='#31a354', label='Seasonal (20일 주기 월간 계절성)')
    axes[2].legend(loc='upper left')
    
    axes[3].plot(decomp.resid, color='#de2d26', label='Residual (노이즈/거시 외생 충격)')
    axes[3].legend(loc='upper left')
    
    plt.xlabel("거래일", fontsize=12)
    plt.tight_layout()
    plt.savefig("images/04_seasonal_decompose.png", dpi=300)
    plt.close()
    
    # -------------------------------------------------------------
    # 5. [보너스 B] 14거래일 단기 베이스라인 예측 및 한계 분석
    # -------------------------------------------------------------
    test_days = 14
    train = df['Close'].iloc[:-test_days]
    test = df['Close'].iloc[-test_days:]
    
    # 베이스라인 1: 직전 14일 단순 이동평균(Naïve SMA)
    sma_pred_val = train.iloc[-14:].mean()
    sma_preds = pd.Series(sma_pred_val, index=test.index)
    
    # 베이스라인 2: 선형 추세 연장(Linear Drift)
    drift_slope = (train.iloc[-1] - train.iloc[-14]) / 14
    drift_preds = pd.Series([train.iloc[-1] + drift_slope * (i + 1) for i in range(test_days)], index=test.index)
    
    # RMSE 계산
    rmse_sma = np.sqrt(np.mean((test - sma_preds)**2))
    rmse_drift = np.sqrt(np.mean((test - drift_preds)**2))
    
    plt.figure(figsize=(14, 6))
    plt.plot(train.iloc[-60:].index, train.iloc[-60:], label='학습 구간 실제 환율 (최근 60일)', color='#555555')
    plt.plot(test.index, test, label='테스트 구간 실제 환율 (14일)', color='black', linewidth=2.5, marker='o')
    plt.plot(test.index, sma_preds, label=f'단순 롤링평균 예측 (RMSE: {rmse_sma:,.1f}원)', color='#e6550d', linestyle='--', linewidth=2)
    plt.plot(test.index, drift_preds, label=f'단기 추세연장 예측 (RMSE: {rmse_drift:,.1f}원)', color='#2b8cbe', linestyle='-.', linewidth=2)
    
    plt.title("원/달러 환율 14거래일 단기 베이스라인 예측 vs 실제값 비교 (가정과 한계 검증)", fontsize=15, fontweight='bold', pad=12)
    plt.xlabel("거래일", fontsize=12)
    plt.ylabel("환율 (원/달러)", fontsize=12)
    plt.legend(loc='lower left', frameon=True)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig("images/05_baseline_forecast.png", dpi=300)
    plt.close()

    print("[OK] 모든 시각화 이미지 5종이 images/ 디렉토리에 저장되었습니다.")

def print_summary_statistics(df):
    """핵심 통계치를 출력합니다."""
    print("\n" + "="*50)
    print("📊 [원/달러 환율 분석 핵심 통계치 요약]")
    print("="*50)
    max_p = df['Close'].max()
    max_d = df['Close'].idxmax().strftime("%Y-%m-%d")
    min_p = df['Close'].min()
    min_d = df['Close'].idxmin().strftime("%Y-%m-%d")
    start_p = df['Close'].iloc[0]
    end_p = df['Close'].iloc[-1]
    total_ret = ((end_p - start_p) / start_p) * 100
    
    print(f"- 분석 기간 시작 환율 (2023-01-02): {start_p:,.2f}원")
    print(f"- 분석 기간 종료 환율 (2024-12-30): {end_p:,.2f}원")
    print(f"- 2개년 총 환율 상승률: +{total_ret:.2f}% (원화 가치 절하)")
    print(f"- 52주 최고 환율: {max_p:,.2f}원 ({max_d})")
    print(f"- 52주 최저 환율: {min_p:,.2f}원 ({min_d})")
    print(f"- 일일 최대 상승폭: +{df['Daily_Return'].max():.2f}% ({df['Daily_Return'].idxmax().strftime('%Y-%m-%d')})")
    print(f"- 일일 최대 하락폭: {df['Daily_Return'].min():.2f}% ({df['Daily_Return'].idxmin().strftime('%Y-%m-%d')})")
    print("="*50 + "\n")

if __name__ == "__main__":
    setup_environment()
    df = fetch_and_clean_data()
    df = feature_engineering(df)
    generate_visualizations(df)
    print_summary_statistics(df)
