# AI Trend Analysis Dashboard

CSV 데이터를 기반으로 AI 채용 수요와 개발자 AI 도구 사용률을 분석하는 Python 프로젝트입니다.

정적 시각화 이미지와 4페이지 PDF 리포트를 생성할 수 있으며, Flask 웹 대시보드에서 차트와 원본 집계 데이터를 탭별로 확인할 수도 있습니다.

## 주요 기능

- 월별 Indeed AI 채용공고 비중 추이
- 직무별 AI 스킬 수요 비교
- Stack Overflow 개발자 AI 도구 사용률 추이
- 2025년 국가별 LinkedIn AI Hiring Index 비교
- 3개월 이동평균(3MA) 계산
- 차트별 데이터 테이블 제공
- 정적 PNG 대시보드 생성
- 4페이지 PDF 리포트 생성
- Flask와 Chart.js 기반 웹 대시보드 제공

## 프로젝트 구조

```text
.
├── ai_trend_dataset_template.csv       # 분석 원본 데이터
├── ai_trend_visual.py                  # 정적 그래프와 PDF 생성 스크립트
├── app.py                              # Flask 웹 서버
├── templates/
│   └── index.html                      # 웹 대시보드 화면
├── output/
│   ├── ai_trend_visualization.png      # 생성되는 통합 그래프 이미지
│   └── ai_trend_report_4pages.pdf      # 생성되는 4페이지 PDF
└── .venv/                              # 프로젝트 가상환경
```

## 실행 환경

- Python 3.12 권장
- pandas
- matplotlib
- seaborn
- numpy
- Flask

## 설치

PowerShell에서 프로젝트 폴더로 이동한 뒤 가상환경을 생성합니다.

```powershell
cd C:\Temp\data_trend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install pandas matplotlib seaborn numpy flask
```

이미 `.venv`가 있다면 패키지 설치 명령만 실행하면 됩니다.

## 정적 그래프와 PDF 생성

```powershell
.\.venv\Scripts\python.exe ai_trend_visual.py
```

실행이 완료되면 다음 파일이 `output` 폴더에 생성됩니다.

- `output/ai_trend_visualization.png`
- `output/ai_trend_report_4pages.pdf`

## 웹 대시보드 실행

```powershell
.\.venv\Scripts\python.exe app.py
```

브라우저에서 다음 주소를 엽니다.

```text
http://127.0.0.1:5000
```

웹 대시보드에는 4개의 탭이 표시됩니다.

- Indeed Trend
- Occupation
- Stack Overflow
- Country

각 탭을 선택하면 해당 그래프와 집계 데이터 테이블이 표시됩니다.

## 웹 API

대시보드 데이터는 다음 API에서 JSON으로 제공합니다.

```text
GET /api/data
```

예를 들어 서버 실행 후 브라우저에서 다음 주소를 열면 차트 데이터를 직접 확인할 수 있습니다.

```text
http://127.0.0.1:5000/api/data
```

## 데이터 처리 흐름

```text
CSV 파일
  -> pandas DataFrame 로드
  -> 날짜 형식 변환
  -> 월별 평균 및 직무·국가별 집계
  -> 3개월 이동평균 계산
  -> PNG/PDF 생성 또는 JSON API 응답
  -> Chart.js 웹 차트 렌더링
```

## 주요 데이터 컬럼

- `year_month`: 월별 기준 날짜
- `occupation`: 직무명
- `country`: 국가명
- `source_indeed_ai_job_share`: Indeed AI 관련 채용공고 비중
- `source_so_ai_use_rate`: Stack Overflow AI 도구 사용률
- `source_linkedin_ai_hiring_index`: LinkedIn AI 채용 지수

## 참고 사항

- 웹 대시보드는 실행 시 CSV 파일을 읽어 데이터를 계산합니다.
- CSV 파일을 수정하면 다음 요청 또는 서버 재시작 이후 변경된 분석 결과가 반영됩니다.
- Chart.js는 CDN에서 로드되므로 웹 대시보드 실행 시 인터넷 연결이 필요할 수 있습니다.
- Flask 개발 서버는 `debug=True`로 실행되며, 운영 환경에서는 별도의 WSGI 서버 사용을 권장합니다.
