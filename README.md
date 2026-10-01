# AI Trend Analysis Dashboard

CSV 데이터를 기반으로 AI 채용 수요와 개발자 AI 도구 사용률을 분석하는 Python 프로젝트입니다.

정적 6패널 시각화 이미지, 분석 보고서와 6페이지 PDF를 생성할 수 있으며, Flask 웹 대시보드에서 차트와 집계 데이터를 탭별로 확인할 수도 있습니다.

**저장소:** https://github.com/bigpark61/data_trend

**데이터 원문:** [Indeed Hiring Lab](https://www.hiringlab.org/) · [Stack Overflow Survey](https://survey.stackoverflow.co/2024/ai) · [LinkedIn Economic Graph](https://economicgraph.linkedin.com/)

**분석 보고서:** [06_REPORT.md](./06_REPORT.md) — 지표 정의, 원본 샘플, 품질 규칙, 결과, 출처 및 한계를 포함합니다.

## 주요 기능

- 월별 Indeed AI 채용공고 비중 추이
- 직무별 AI 스킬 수요 비교
- Stack Overflow 개발자 AI 도구 사용률 추이
- 2025년 국가별 LinkedIn AI Hiring Index 비교
- 3개월 이동평균(3MA) 계산
- 월별 전월 대비 변화율 및 12개월 계절분해(추세·계절성·잔차)
- 공통 입력 검증·집계 모듈을 정적 그래프와 Flask API에서 재사용
- 차트별 데이터 테이블 제공
- 정적 PNG 대시보드 생성
- 6페이지 PDF 리포트 생성
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
│   └── ai_trend_analysis_6pages.pdf    # 생성되는 6페이지 PDF
├── ai_trend_data.py                   # 공통 CSV 검증·시계열 집계
├── 06_REPORT.md                       # 수치 및 데이터에 맞춰 생성되는 분석 보고서
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
- `output/ai_trend_analysis_6pages.pdf`
- `06_REPORT.md`

PNG는 150 dpi의 6패널 대시보드이며, 실행 시 정확한 픽셀 크기와 각 패널의 캡션은 `06_REPORT.md`에 기록됩니다. 6개 패널은 (1) Indeed 원자료·3MA 추세, (2) 직무별 비교, (3) Stack Overflow 사용률·3MA, (4) 국가별 지수, (5) Indeed 전월 변화율, (6) Indeed 가법 계절분해를 보여줍니다.

## 웹 대시보드 실행

```powershell
.\.venv\Scripts\python.exe app.py
```

브라우저에서 다음 주소를 엽니다.

```text
http://127.0.0.1:5000
```

웹 대시보드에는 6개의 탭이 표시됩니다.

- Indeed Trend
- Occupation
- Stack Overflow
- Country
- Monthly Change
- Decomposition

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
  -> ai_trend_data.load_dataset (헤더 정리, 날짜·키·수치 검증)
  -> ai_trend_data.prepare_data (월별/직무/국가 집계, 3MA, 전월 변화율, 분해)
  -> ai_trend_visual.create_ai_trend_dashboard / create_analysis_pdf / create_analysis_report
  -> app.build_charts -> GET /api/data -> templates/index.html 렌더링
```

## 데이터 샘플

현재 저장된 CSV는 864개 레코드(36개월×6개 국가×4개 직무)입니다. 첫 5행의 핵심 지표:

| year_month | Indeed AI job share (%) | Stack Overflow AI use rate (%) | LinkedIn AI hiring index |
|---|---:|---:|---:|
| Jan-23 | 9.22 | 81.9 | 110.4 |
| Jan-23 | 6.77 | 74.3 | 128.1 |
| Jan-23 | 6.92 | 64.3 | 108.3 |
| Jan-23 | 7.00 | 82.6 | 123.1 |
| Jan-23 | 7.42 | 80.8 | 101.3 |

분석 보고서는 실행 시 실제 파일의 전체 행 수와 첫 10행 샘플로 갱신됩니다. CSV 행 수가 변경되면 위의 요약 표도 함께 갱신하세요.

## 분석 규칙

- 결측 지표는 보간·대체하지 않습니다. 부분 관측 월은 유효값 평균, 전체 결측 월은 결측으로 남깁니다. 날짜·키 결측, 잘못된 날짜·숫자 및 날짜·국가·직무 중복은 오류로 처리합니다.
- 이상치는 칼럼별 `Q1−1.5×IQR`/`Q3+1.5×IQR` 기준으로 표시만 하며 제거·대체하지 않습니다.
- 변화율은 `(현재월/전월−1)×100`; 분모가 작을 때 민감하고 첫 달은 계산되지 않습니다. 12개월 가법 분해의 2×12 중심 이동평균 추세는 양 끝 6개월에서 정의되지 않습니다.
- 현재 데이터는 기술통계로, 임의 표본 추출 설계가 확인되지 않아 p-value·모집단 신뢰구간을 주장하지 않습니다. `06_REPORT.md`의 2.5–97.5 백분위는 관측 범위 요약입니다.

## 출처

- [Indeed Hiring Lab](https://www.hiringlab.org/)
- [Stack Overflow Developer Survey – AI](https://survey.stackoverflow.co/2024/ai)
- [LinkedIn Economic Graph](https://economicgraph.linkedin.com/)
- [Stanford AI Index](https://aiindex.stanford.edu/report/)

위 링크는 원문 출처 안내입니다. CSV 각 행의 원자료 URL·추출일·변환 과정은 저장소에 보존되어 있지 않으므로 각 값의 직접적인 원문 계보를 보증하지 않습니다.

## 테스트

```powershell
.\.venv\Scripts\python.exe -m unittest test_ai_trend_data.py
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
