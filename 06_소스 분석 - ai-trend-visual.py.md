
## `ai_trend_visual.py` 프로그램 소스 설명

이 코드는 “AI 트렌드 데이터 CSV를 읽어서 시각화 그래프와 PDF 보고서를 만드는 프로그램”입니다. 전체적으로는 3개 큰 부분으로 나눌 수 있습니다.

1. 모듈 불러오기
2. 데이터 전처리
3. 그래프 생성 및 PDF 저장
4. 실행부

---

## 1) 모듈 import 영역

```python
import matplotlib
matplotlib.use('Agg')  # Headless 환경 설정
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import seaborn as sns
import pandas as pd
import numpy as np
import os
```

### 역할
- matplotlib
  - 그래프를 그리는 핵심 라이브러리
- matplotlib.use('Agg')
  - 화면 없이 백그라운드에서 그래프를 생성하도록 설정
  - 서버 환경이나 비대화형 환경에서 유용
- matplotlib.pyplot as plt
  - 플롯 생성, 축/제목 설정, 저장 등을 담당
- PdfPages
  - 여러 페이지 PDF를 만드는 기능
- seaborn
  - 그래프 스타일을 깔끔하게 정리하는 라이브러리
- pandas
  - CSV 파일 읽기, 집계, 시계열 처리
- numpy
  - 숫자 연산용
- os
  - 파일 경로 처리

---

## 2) 데이터 전처리 함수: _prepare_data

```python
def _prepare_data(data_path):
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"데이터 파일을 찾을 수 없습니다: {data_path}")

    df = pd.read_csv(data_path)
    df['datetime'] = pd.to_datetime(df['year_month'])
```

### 역할
- 입력 파일이 존재하는지 먼저 확인
- CSV 파일을 읽어서 pandas DataFrame으로 변환
- year_month 컬럼을 datetime 형식으로 바꿈

### 이유
- 월별 데이터는 날짜 기준으로 정렬하거나 집계할 때 필요
- 시계열 분석을 위해서 datetime 변환이 중요

---

### 월별 집계

```python
df_monthly = df.groupby('datetime')[[
    'source_indeed_ai_job_share',
    'source_so_ai_use_rate',
    'source_linkedin_ai_hiring_index'
]].mean().reset_index()
```

### 역할
- 날짜별로 평균값을 계산
- 예:
  - Indeed AI 채용공고 비중
  - Stack Overflow AI 사용률
  - LinkedIn AI 채용 지수

### 결과
- 각 월별 대표값이 만들어짐
- 차트 1, 3에서 사용

---

### 이동평균 계산

```python
df_monthly['ai_job_share_3ma'] = df_monthly['source_indeed_ai_job_share'].rolling(window=3, min_periods=1).mean()
df_monthly['so_ai_use_rate_3ma'] = df_monthly['source_so_ai_use_rate'].rolling(window=3, min_periods=1).mean()
```

### 역할
- 3개월 이동평균(3MA)을 계산
- 그래프에 추세선을 넣기 위해 사용
- 단기 변동을 완화하고 흐름을 더 잘 보여줌

### 의미
- 월별 데이터는 진동이 심할 수 있어
- 3개월 평균으로 전체 추세를 부드럽게 표현

---

### 직무별 데이터 집계

```python
df_occ = df.groupby(['datetime', 'occupation'])['source_indeed_ai_job_share'].mean().unstack()
```

### 역할
- 직무별 AI 채용공고 비중을 시간에 따라 비교
- occupation을 기준으로 여러 라인을 한 그래프에 그리기 위한 구조 생성

### 결과
- DataFrame 형태로 각 직무가 컬럼이 됨

---

### 2025년 국가별 지수 집계

```python
df_country_2025 = df[df['year_month'].str.startswith('2025')].groupby('country')['source_linkedin_ai_hiring_index'].mean().sort_values(ascending=False)
```

### 역할
- 2025년 데이터만 추출
- 국가별 평균 AI 채용 지수 계산
- 값이 높은 순서대로 정렬

### 결과
- 국가 비교 막대그래프용 데이터 생성

---

## 3) 대시보드 생성 함수: create_ai_trend_dashboard

```python
def create_ai_trend_dashboard(data_path, output_image_path):
```

### 역할
- 데이터 입력 경로와 결과 이미지 저장 경로를 받아
- 4개 차트가 들어간 전체 대시보드 이미지를 생성

---

### 스타일 설정

```python
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False
sns.set_theme(style='whitegrid', font='DejaVu Sans', palette='colorblind')
```

### 역할
- 그래프 기본 폰트 설정
- 한글이 없지만 깨짐 방지용
- seaborn 테마로 깔끔한 배경과 격자 설정

---

### 2x2 subplot 구성

```python
fig, axes = plt.subplots(2, 2, figsize=(15, 11))
```

### 역할
- 전체 그래프를 2행 2열 구조로 배치
- 4개의 차트가 같은 큰 그림 안에 들어감

---

### 차트 1: Indeed AI 채용공고 비중 추이

```python
ax1 = axes[0, 0]
ax1.plot(df_monthly['datetime'], df_monthly['source_indeed_ai_job_share'], ...)
ax1.plot(df_monthly['datetime'], df_monthly['ai_job_share_3ma'], ...)
ax1.set_title('1. Indeed AI Job Share Trend (%)', ...)
ax1.set_ylabel('Share (%)')
ax1.legend(...)
ax1.set_ylim(6.5, 9.5)
```

### 역할
- 월별 Indeed AI 채용공고 비중 추이
- 원본 데이터와 3개월 이동평균 비교
- 시계열 흐름을 보여줌

---

### 차트 2: 직무별 AI 요구 비중 비교

```python
ax2 = axes[0, 1]
for occ in df_occ.columns:
    ax2.plot(df_occ.index, df_occ[occ], label=occ, linewidth=2)
```

### 역할
- 직무별 데이터 비교
- 예: AI·ML Engineer, Data Scientist, Software Developer 등
- 각 직무의 AI 비중 변화를 선으로 표현

---

### 차트 3: Stack Overflow 개발자 AI 도구 사용률

```python
ax3 = axes[1, 0]
ax3.plot(df_monthly['datetime'], df_monthly['source_so_ai_use_rate'], ...)
ax3.plot(df_monthly['datetime'], df_monthly['so_ai_use_rate_3ma'], ...)
```

### 역할
- 개발자들의 AI 도구 사용률 추이 표현
- 사용자들이 실제로 AI를 얼마나 쓰는지 파악

---

### 차트 4: 국가별 LinkedIn AI 채용 지수

```python
ax4 = axes[1, 1]
bars = ax4.bar(df_country_2025.index, df_country_2025.values, ...)
```

### 역할
- 국가별 AI 채용 지수 비교
- 막대그래프로 직관적으로 비교 가능
- 각 막대 위에 값 라벨 추가

```python
for bar in bars:
    height = bar.get_height()
    ax4.text(...)
```

### 역할
- 각 바 위에 숫자 표시
- 시각적으로 더 이해하기 쉽게 함

---

### 공통 레이아웃 정리

```python
sns.despine(fig=fig)
plt.tight_layout(pad=2.0, rect=[0, 0.02, 1, 0.95])
fig.text(...)
```

### 역할
- 불필요한 축 장식 제거
- 그래프 간 간격을 깔끔하게 정리
- 출처 문구를 하단에 추가

---

### 이미지 저장

```python
plt.savefig(output_image_path, dpi=150, bbox_inches='tight')
plt.close()
print(f"[성공] ...")
```

### 역할
- 최종 이미지를 저장
- bbox_inches='tight'로 여백을 줄여서 깔끔한 출력
- 파일 생성 후 메모리 정리

---

## 4) PDF 다중 페이지 생성 함수: create_four_page_report

```python
def create_four_page_report(data_path, output_pdf_path):
```

### 역할
- 같은 데이터로 페이지를 4개로 나눠 PDF를 만드는 함수

---

### PdfPages 사용

```python
with PdfPages(output_pdf_path) as pdf:
```

### 역할
- 여러 페이지를 하나의 PDF에 저장함
- 각 페이지를 순서대로 추가 가능

---

### 페이지 1~4 구성
- Page 1: Indeed AI 채용공고 비중 추이
- Page 2: 직무별 AI 요구 비중
- Page 3: Stack Overflow AI 사용률
- Page 4: 국가별 LinkedIn AI 채용 지수

각 페이지는 `plt.subplots()`로 개별 그림을 만들고
`pdf.savefig(fig)`로 PDF에 저장합니다.

---

## 5) 실행부: if __name__ == '__main__':

```python
if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(base_dir, 'ai_trend_dataset_template.csv')
    output_dir = os.path.join(base_dir, 'output')
    os.makedirs(output_dir, exist_ok=True)

    output_file = os.path.join(output_dir, 'ai_trend_visualization.png')
    output_pdf = os.path.join(output_dir, 'ai_trend_report_4pages.pdf')

    create_ai_trend_dashboard(data_file, output_file)
    create_four_page_report(data_file, output_pdf)
```

### 역할
- 현재 파일이 직접 실행될 때만 동작
- 현재 폴더 기준으로 데이터 파일 경로를 설정
- output 폴더 자동 생성
- PNG 대시보드와 4페이지 PDF를 모두 생성

---

## 전체 구조 요약

- `_prepare_data()`
  - CSV 읽기 + 전처리 + 집계
- `create_ai_trend_dashboard()`
  - 4개 그래프를 한 번에 그려 PNG 저장
- `create_four_page_report()`
  - 각 그래프를 별도 페이지로 PDF 생성
- `__main__`
  - 전체 실행과 경로 설정

---

원하시면 다음으로 이어서:
- “이 코드를 모듈별로 더 세분화해서 설명”
- “각 함수 코드 한 줄씩 해석”
- “이 프로그램의 구조도를 그려서 설명”

까지 해드릴게요.

## 프로그램 구조도

아래처럼 흐름을 이해하면 전체 로직이 한눈에 보입니다.

```mermaid
flowchart TD
    A[CSV 데이터 파일<br/>ai_trend_dataset_template.csv] --> B[_prepare_data()]
    B --> B1[파일 존재 확인]
    B --> B2[CSV 읽기]
    B --> B3[year_month → datetime 변환]
    B --> B4[월별 평균 집계]
    B --> B5[3개월 이동평균 계산]
    B --> B6[직무별 집계]
    B --> B7[2025년 국가별 집계]

    B4 --> C1[차트 1: Indeed AI Job Share Trend]
    B6 --> C2[차트 2: AI Skill Demand by Occupation]
    B4 --> C3[차트 3: Stack Overflow Usage Trend]
    B7 --> C4[차트 4: Country Hiring Index]

    C1 --> D[create_ai_trend_dashboard()]
    C2 --> D
    C3 --> D
    C4 --> D

    D --> E[2x2 subplot 구성]
    E --> F[그래프 스타일 적용]
    F --> G[PNG 이미지 저장<br/>output/ai_trend_visualization.png]

    B --> H[create_four_page_report()]
    H --> H1[Page 1]
    H --> H2[Page 2]
    H --> H3[Page 3]
    H --> H4[Page 4]
    H1 --> I[PDF 저장<br/>output/ai_trend_report_4pages.pdf]
    H2 --> I
    H3 --> I
    H4 --> I

    J[__main__] --> K[경로 설정]
    K --> L[output 폴더 생성]
    L --> M[create_ai_trend_dashboard()]
    L --> N[create_four_page_report()]
```

---

## 설명

### 1. 입력
- 프로그램은 CSV 파일을 기준으로 동작합니다.
- 입력 파일:
  - `ai_trend_dataset_template.csv`

### 2. 전처리 단계
- `_prepare_data()`
  - 데이터 파일 검증
  - 날짜 변환
  - 월별 집계
  - 3개월 이동평균 계산
  - 직무별/국가별 집계

이 단계가 가장 핵심입니다.  
왜냐하면 그래프를 그리기 전에 “정리된 데이터 구조”를 만들어야 하기 때문입니다.

---

### 3. 대시보드 생성
- `create_ai_trend_dashboard()`
  - 2x2 형태의 전체 차트 레이아웃 생성
  - 4개 그래프를 한 번에 그리기
  - 최종적으로 이미지 파일로 저장

예:
- 차트 1: Indeed AI 채용공고 비중
- 차트 2: 직무별 AI 요구 비중
- 차트 3: Stack Overflow AI 사용률
- 차트 4: 국가별 LinkedIn AI 채용 지수

---

### 4. PDF 보고서 생성
- `create_four_page_report()`
  - 각 차트를 페이지별로 분리
  - 하나의 PDF 파일로 묶음
  - 발표용 문서로 사용 가능

---

### 5. 실행 시작점
- `if __name__ == '__main__':`
  - 프로그램을 직접 실행할 때 시작
  - 경로 설정
  - output 폴더 생성
  - PNG + PDF 생성 호출

---

## 실제 의미로 보면

이 프로그램은 단순한 “그래프 코드”가 아니라 다음 흐름으로 동작합니다.

```text
CSV 데이터
→ 데이터 정리
→ 시계열/집계 처리
→ 그래프 생성
→ 이미지 저장
→ PDF 보고서 생성
```

즉, 데이터 분석 → 시각화 → 결과물 산출이라는 전체 데이터 분석 파이프라인 구조를 갖고 있습니다.

---

## 한 줄 요약

이 프로그램은:
- 데이터 준비
- 시계열 분석
- 그래프 시각화
- 이미지/PDF 출력

의 4단계 구조를 갖는 데이터 시각화 프로그램입니다.

원하시면 다음으로:
- 이 구조도를 실제 코드 라인 기준으로 더 자세히 매칭해서 설명
- “모듈별 책임 분담표” 형태로 정리
- “업무 흐름도(Flowchart)”처럼 비즈니스 관점으로 설명

까지 해드릴게요.