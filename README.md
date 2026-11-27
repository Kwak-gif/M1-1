# 원/달러(USD/KRW) 환율 시계열 트렌드 및 변동성 분석

AI 응용 학습(AI Native Master) `M1-1` 과제 결과물 저장소입니다.  
2023~2024년 2개년 원/달러 일별 환율(`KRW=X`) 데이터를 바탕으로 추세, 이동평균 수급 흐름, 월별 변동성, 시계열 분해, 단기 베이스라인 예측 및 Streamlit 탐색 대시보드를 구현했습니다.

- 상세 분석 결과 및 인사이트: [REPORT.md](REPORT.md)

---

## 저장소 구성

```text
M1-1/
├── README.md                          # 프로젝트 개요 및 실행 방법
├── REPORT.md                          # 최종 분석 리포트 (시각화, 인사이트, AI 사용 로그)
├── analysis.py                        # 데이터 수집, 전처리, 차트 5종 생성 스크립트
├── analysis.ipynb                     # 실행 결과(출력·그래프)가 저장된 Jupyter Notebook
├── app.py                             # Streamlit 기반 인터랙티브 환율 대시보드
├── requirements.txt                   # 실행에 필요한 Python 패키지 목록
├── data/
│   ├── usdkrw_2023_2024.csv           # 원본 환율 일봉 데이터 (521거래일)
│   └── usdkrw_processed.csv           # 이동평균, 등락률, 변동성, 급변동 플래그 포함 데이터
└── images/
    ├── 01_exchange_rate_trend.png     # 2개년 환율 추이 및 1,300/1,400원 기준선
    ├── 02_moving_average.png          # 20일·60일 이동평균선 및 교차 구간
    ├── 03_monthly_volatility.png      # 월별 평균 롤링 변동성(20일 표준편차)
    ├── 04_seasonal_decompose.png      # 시계열 가법 분해 (추세·계절성·잔차)
    ├── 05_baseline_forecast.png       # 14거래일 단기 베이스라인 예측 비교
    ├── 06_dashboard_overview.png      # Streamlit 대시보드 전체 기간 화면
    ├── 07_dashboard_scenario1.png     # 대시보드 시나리오 1 (2024년 4분기 확대)
    └── 08_dashboard_scenario2.png     # 대시보드 시나리오 2 (10일·30일 이평선 비교)
```

---

## 실행 환경 및 방법

Python 3.10 이상 환경에서 아래 순서대로 실행할 수 있습니다.

### 1. 패키지 설치
```bash
pip install -r requirements.txt
```

### 2. 데이터 수집 및 분석 차트 생성
스크립트 또는 노트북 중 편한 방식으로 실행합니다.

```bash
# Python 스크립트 실행
python analysis.py
```

```bash
# Jupyter Notebook으로 확인
jupyter notebook analysis.ipynb
```

### 3. Streamlit 대시보드 실행 (보너스 과제)
```bash
streamlit run app.py
```
실행 후 브라우저에서 `http://localhost:8501`에 접속해 조회 기간과 이동평균 일수를 조절할 수 있습니다. URL 쿼리 파라미터로 특정 시나리오 화면을 바로 여는 것도 가능합니다.

- 시나리오 1 (2024년 4분기 집중 보기): `http://localhost:8501/?start=2024-10-01&end=2024-12-30`
- 시나리오 2 (10일·30일 이평선 민감도 비교): `http://localhost:8501/?short=10&long=30`

---

## 주요 수치 요약

| 항목 | 수치 |
| :--- | :--- |
| 분석 기간 및 건수 | 2023-01-02 ~ 2024-12-30 (521거래일, 결측치 0건) |
| 시작 / 종료 종가 | 1,260.91원 → 1,472.80원 (+16.80%) |
| 기간 최저 / 최고 종가 | 1,221.95원 (2023-02-02) / 1,472.80원 (2024-12-30) |
| 기간 장중 최저 / 최고 | 1,216.0원 / 1,487.04원 (2024-12-27) |
| 일일 최대 상승 / 하락 | +2.07% (2023-12-19) / -1.98% (2024-11-08) |
| 월별 변동성 최고 / 최저 | 2023-03 (0.75%) / 2024-03 (0.38%), 평균 0.56% |
| 급변동 이상치 (±1.5% 이상) | 총 11거래일 |

---

## 데이터 출처 및 유의사항

- 데이터 출처: Yahoo Finance (`yfinance` API, 티커 `KRW=X`)
- 본 저장소의 데이터와 분석 결과는 학습 및 비상업적 연구 목적으로만 작성되었으며, 상업적 재배포를 금지합니다.
