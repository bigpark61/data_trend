
## `app.py` 프로그램 소스 분석

이 파일은 Flask 기반의 웹 서버입니다.  
핵심 역할은 다음 3가지입니다.

1. CSV 데이터를 읽어서 정리한다
2. 4개 차트 데이터를 JSON 형태로 만든다
3. 웹 페이지와 API를 제공해서 브라우저에서 차트를 보여준다

---

## 1) 모듈 import 영역

```python
from flask import Flask, jsonify, send_from_directory
import pandas as pd
import os
```

### 역할
- Flask
  - 웹 서버를 만드는 핵심 라이브러리
- jsonify
  - Python 객체를 JSON 형태로 변환
- send_from_directory
  - HTML 파일을 브라우저로 전달
- pandas
  - CSV 처리 및 데이터 분석
- os
  - 파일 경로 처리

---

## 2) Flask 앱 초기화

```python
app = Flask(__name__, static_folder='static')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, 'ai_trend_dataset_template.csv')
```

### 역할
- Flask 앱 객체 생성
- 현재 파일 위치를 기준으로 데이터 파일 경로를 설정
- 결국 이 프로그램은 현재 폴더 안의 CSV를 기준으로 동작합니다

### 의미
- `BASE_DIR` = 현재 프로젝트 폴더 경로
- `DATA_PATH` = 데이터 파일 경로
- 예: 현재 폴더 안의 `ai_trend_dataset_template.csv`

---

## 3) 데이터 로드 함수: load_dataframe

```python
def load_dataframe():
    df = pd.read_csv(DATA_PATH)
    df['datetime'] = pd.to_datetime(df['year_month'])
    return df
```

### 역할
- CSV 파일을 읽어 DataFrame으로 변환
- `year_month` 컬럼을 날짜형 데이터로 변환

### 왜 필요한가
- 월별 데이터를 시계열로 다루려면 `datetime` 타입이 필요합니다
- 그래프 x축을 시간 순서로 정렬하고, 월별 집계를 할 수 있습니다

---

## 4) 차트 데이터 구성 함수: build_charts

```python
def build_charts():
    df = load_dataframe()
```

### 역할
- 데이터 읽기
- 이후 각 차트에 필요한 집계 데이터 생성

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
- 날짜별로 평균값 계산
- 각 월의 대표값을 만든다

### 사용 목적
- Indeed AI 비중 추이
- Stack Overflow AI 사용률
- LinkedIn AI 채용 지수

이 값들을 기준으로 그래프를 생성합니다

---

### 이동평균 계산

```python
df_monthly['ai_job_share_3ma'] = df_monthly['source_indeed_ai_job_share'].rolling(window=3, min_periods=1).mean()
df_monthly['so_ai_use_rate_3ma'] = df_monthly['source_so_ai_use_rate'].rolling(window=3, min_periods=1).mean()
```

### 역할
- 3개월 이동평균 계산
- 그래프에서 추세선을 표현하기 위해 사용
- 초반 변동을 완화해서 흐름을 보기 쉽게 함

---

### 직무별 집계

```python
df_occ = df.groupby(['datetime', 'occupation'])['source_indeed_ai_job_share'].mean().unstack()
```

### 역할
- 직무별 AI 채용공고 비중을 비교 가능하도록 변환
- 각 직무가 서로 다른 선으로 나타남

---

### 2025년 국가별 집계

```python
df_country_2025 = df[df['year_month'].str.startswith('2025')].groupby('country')['source_linkedin_ai_hiring_index'].mean().sort_values(ascending=False)
```

### 역할
- 2025년 데이터만 추출
- 국가별 LinkedIn AI 채용 지수를 평균 계산
- 순위를 정렬

---

## 5) 차트 배열 생성

```python
charts = [
    {...},
    {...},
    {...},
    {...}
]
```

### 역할
- 각 탭에 대한 차트 정보들을 리스트로 저장
- 브라우저가 읽을 수 있는 JSON 구조로 구성

---

### 차트 1: Indeed Trend

```python
{
    'id': 'indeed-trend',
    'tabLabel': 'Indeed Trend',
    'title': 'Indeed AI Job Share Trend (%)',
    'type': 'line',
    'labels': df_monthly['datetime'].dt.strftime('%Y-%m').tolist(),
    'datasets': [...]
}
```

### 역할
- 선 그래프로 월별 추세를 표현
- raw data + 3MA 기준값을 같이 보여줌
- 표(table)도 같이 넣어 숫자 확인 가능

---

### 차트 2: Occupation

```python
{
    'id': 'occupation',
    'tabLabel': 'Occupation',
    'title': 'AI Skill Demand by Occupation (%)',
    'type': 'line',
    ...
}
```

### 역할
- 직무별 커브 비교
- 여러 직무를 한 그래프에 동시에 표현

---

### 차트 3: Stack Overflow

```python
{
    'id': 'stackoverflow',
    'tabLabel': 'Stack Overflow',
    'title': 'Stack Overflow Developer AI Tool Usage Trend (%)',
    'type': 'line',
    ...
}
```

### 역할
- 개발자 AI 도구 사용률 트렌드 표시

---

### 차트 4: Country

```python
{
    'id': 'country',
    'tabLabel': 'Country',
    'title': 'LinkedIn AI Hiring Index by Major Country (2025)',
    'type': 'bar',
    ...
}
```

### 역할
- 국가별 AI 채용 지수를 막대 그래프로 비교
- 그래프 아래에 표로 값도 같이 제공

---

## 6) 표 데이터(table) 추가

각 차트 객체 안에는 `table` 항목이 포함됩니다.

예:

```python
'table': {
    'headers': ['Date', 'Monthly raw data', '3-month moving average (3MA)'],
    'rows': [
        [date, round(raw, 2), round(ma, 2)]
        ...
    ]
}
```

### 역할
- 그래프 아래 표를 만들기 위한 데이터
- 항목별 실제 숫자를 함께 제공
- “시각화 + 수치”를 함께 볼 수 있도록 함

---

## 7) API 엔드포인트: / 와 /api/data

### 루트 페이지 제공

```python
@app.route('/')
def index():
    return send_from_directory('templates', 'index.html')
```

### 역할
- 브라우저에서 http://127.0.0.1:5000 접속 시
- `index.html` 파일을 보여줌

---

### 데이터 API 제공

```python
@app.route('/api/data')
def data_api():
    return jsonify(build_charts())
```

### 역할
- 브라우저가 `fetch('/api/data')`로 호출하면
- 차트 JSON 데이터를 반환
- JavaScript가 이를 읽어 화면에 렌더링

### 중요한 점
- 이 구조는 서버와 프론트엔드가 분리되어 있음
- Python이 데이터만 제공
- HTML/JS가 차트를 그리는 구조

---

## 8) 실행 코드

```python
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
```

### 역할
- Flask 서버 실행
- 외부 접속 허용
- 포트 5000에서 실행
- 디버그 모드 활성화

즉, 서버가 가동되면 웹 페이지가 열리게 됩니다.

---

## 전체 흐름 요약

```text
CSV 파일
   ↓
load_dataframe()
   ↓
build_charts()
   ↓
차트 JSON 생성
   ↓
/api/data API 제공
   ↓
HTML/JS로 차트 렌더링
   ↓
브라우저에서 탭별 차트 표시
```

---

## 한 줄 요약

이 프로그램은 “CSV 데이터를 읽고, 분석용 집계를 만들고, 웹 API로 전달하며, 브라우저에서 탭 기반 차트와 표를 보여주는 Flask 웹 대시보드”입니다.

원하시면 다음으로 이어서:
- 이 파일을 “프론트엔드/백엔드 역할로 분리해서 설명”
- “각 함수의 책임을 표로 정리”
- “실제 동작 순서를 단계별로 설명”

까지 해드릴게요.

Compacted conversation실제 실행 흐름을 코드 기준으로 순서대로 정리해보겠습니다. 관련 파일을 확인해서 실행 경로와 데이터 흐름을 정확히 설명드릴게요.

Read 

Read , lines 1 to 260

Read , lines 261 to 282

## 실제 동작 순서: 단계별 흐름

코드상으로는 아래 순서대로 동작합니다.

1. 서버 실행
   - `app.py`에서 `if __name__ == '__main__':` 블록이 실행됩니다.
   - 그 안의 `app.run(host='0.0.0.0', port=5000, debug=True)`가 호출되어 Flask 서버가 켜집니다.
   - 결과적으로 브라우저에서 `http://127.0.0.1:5000`으로 접속할 수 있게 됩니다.

2. 브라우저가 메인 페이지 요청
   - 브라우저가 `/` 경로에 접근하면 Flask의 `index()` 함수가 실행됩니다.
   - 이 함수는 `index.html` 파일을 전달합니다.
   - 즉, 웹 페이지 HTML이 사용자 화면에 뜹니다.

3. HTML이 로드되고 JavaScript 실행
   - `index.html` 안에는 Chart.js 라이브러리와 JavaScript 코드가 들어 있습니다.
   - 페이지 로딩 직후 `loadData()` 함수가 실행됩니다.

4. JavaScript가 JSON 데이터 요청
   - `loadData()`는 `fetch('/api/data')`를 호출합니다.
   - 이 요청은 Flask의 `/api/data` 라우트로 전달됩니다.

5. 서버가 CSV를 읽어 차트 데이터 생성
   - `app.py`의 `data_api()` 함수가 호출됩니다.
   - 이 함수는 `build_charts()`를 호출합니다.
   - `build_charts()`는 먼저 `load_dataframe()`를 실행합니다.
   - `load_dataframe()`는 `ai_trend_dataset_template.csv`를 읽고,
     `year_month`을 `datetime` 형식으로 변환합니다.
   - 이후 월별 평균, 3개월 이동평균, 직무별 집계, 국가별 집계 등을 계산합니다.

6. 서버가 JSON으로 응답
   - `build_charts()`는 `{'charts': [...]}` 형태의 딕셔너리를 만들고,
   - Flask의 `jsonify()`를 통해 브라우저로 JSON 응답을 보냅니다.
   - 이 JSON에는 4개 차트의 제목, 라벨, 데이터셋, 표(table) 정보가 모두 들어 있습니다.

7. 브라우저가 응답을 받아 탭과 차트 생성
   - JavaScript는 받은 JSON을 `chartConfig`에 저장합니다.
   - `createButtons(chartConfig)`가 실행되어 탭 버튼 4개를 생성합니다.
   - 그다음 `renderChart(activeChartId)`가 실행됩니다.

8. 선택된 차트가 화면에 그림
   - `renderChart()`는 현재 차트 객체를 찾고,
   - Chart.js의 `new Chart(...)`를 사용해 캔버스에 그래프를 그립니다.
   - 동시에 `renderTable(chart)`가 실행되어 해당 차트 아래에 표를 채웁니다.

9. 사용자가 탭을 누르면 다시 렌더링
   - 각 탭 버튼에는 클릭 이벤트가 연결되어 있습니다.
   - 버튼 클릭 시 `renderChart(chartId)`가 다시 호출됩니다.
   - 같은 캔버스를 지우고 새 차트 데이터를 그려서 탭 전환이 이루어집니다.

---

## 핵심 흐름 한 줄 요약

CSV 읽기 → 집계 계산 → JSON API 제공 → HTML/JS가 데이터 수신 → Chart.js로 그래프 표시 → 탭 클릭 시 재렌더링

필요하면 다음으로는 이 흐름을 “시퀀스 다이어그램 형태”로도 정리해드릴게요.