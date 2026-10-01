import os
from datetime import datetime

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import seaborn as sns
from PIL import Image

from ai_trend_data import METRIC_COLUMNS, data_quality_summary, prepare_data


def _configure_plot_style():
    korean_font = r'C:\Windows\Fonts\malgun.ttf'
    font_family = 'Malgun Gothic' if os.path.isfile(korean_font) else 'DejaVu Sans'
    plt.rcParams['font.family'] = font_family
    plt.rcParams['axes.unicode_minus'] = False
    sns.set_theme(style='whitegrid', font=font_family, palette='colorblind')


def _plot_indeed_trend(ax, monthly):
    ax.plot(
        monthly['datetime'],
        monthly['source_indeed_ai_job_share'],
        color='#93c5fd',
        linestyle='--',
        alpha=0.7,
        label='Monthly raw data',
    )
    ax.plot(
        monthly['datetime'],
        monthly['ai_job_share_3ma'],
        color='#2563eb',
        linewidth=2.5,
        label='3-month moving average (3MA)',
    )
    ax.set_title('1. Indeed AI Job Share Trend (%)')
    ax.set_ylabel('Share (%)')
    ax.legend(loc='upper left', frameon=True)


def _plot_occupation(ax, occupation):
    for occ in occupation.columns:
        ax.plot(occupation.index, occupation[occ], label=occ, linewidth=2)
    ax.set_title('2. AI Skill Demand by Occupation (%)')
    ax.set_ylabel('Share (%)')
    ax.legend(loc='upper left', frameon=True, fontsize=9)


def _plot_stackoverflow(ax, monthly):
    ax.plot(
        monthly['datetime'],
        monthly['source_so_ai_use_rate'],
        color='#f87171',
        linestyle='--',
        alpha=0.7,
        label='Monthly usage rate',
    )
    ax.plot(
        monthly['datetime'],
        monthly['so_ai_use_rate_3ma'],
        color='#dc2626',
        linewidth=2.5,
        label='3-month moving average (3MA)',
    )
    ax.set_title('3. Stack Overflow Developer AI Tool Usage (%)')
    ax.set_ylabel('Usage rate (%)')
    ax.legend(loc='lower left', frameon=True)


def _plot_country(ax, country_2025):
    bars = ax.bar(
        country_2025.index,
        country_2025.values,
        color=sns.color_palette('Blues_r', len(country_2025)),
    )
    ax.set_title('4. LinkedIn AI Hiring Index by Country (2025)')
    ax.set_ylabel('AI Hiring Index (2023=100)')
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + 0.8,
            f'{height:.1f}',
            ha='center',
            va='bottom',
            fontsize=9,
            fontweight='bold',
        )


def _plot_pct_change(ax, monthly):
    ax.axhline(0, color='#6b7280', linewidth=1)
    ax.plot(
        monthly['datetime'],
        monthly['ai_job_share_pct_change'],
        color='#7c3aed',
        marker='o',
        markersize=3,
        linewidth=1.5,
    )
    ax.set_title('5. Monthly Change in Indeed AI Job Share')
    ax.set_ylabel('Change from previous month (%)')


def _plot_decomposition(ax, monthly, decomposition):
    ax.plot(
        monthly['datetime'],
        decomposition['observed'],
        color='#93c5fd',
        alpha=0.6,
        label='Observed',
    )
    ax.plot(
        monthly['datetime'],
        decomposition['trend'],
        color='#1d4ed8',
        linewidth=2.5,
        label='Trend (centered 2x12 moving average)',
    )
    component_ax = ax.twinx()
    component_ax.plot(
        monthly['datetime'],
        decomposition['seasonal'],
        color='#f59e0b',
        label='Seasonal',
    )
    component_ax.plot(
        monthly['datetime'],
        decomposition['residual'],
        color='#dc2626',
        alpha=0.65,
        label='Residual',
    )
    ax.set_title('6. Additive Decomposition: Indeed Job Share')
    ax.set_ylabel('Observed / trend (%)')
    component_ax.set_ylabel('Seasonal / residual (share points)')
    lines, labels = ax.get_legend_handles_labels()
    component_lines, component_labels = component_ax.get_legend_handles_labels()
    ax.legend(lines + component_lines, labels + component_labels, loc='best', fontsize=8)


def create_ai_trend_dashboard(data_path, output_image_path):
    _configure_plot_style()
    analysis = prepare_data(data_path)
    fig, axes = plt.subplots(3, 2, figsize=(18, 14))
    fig.suptitle(
        'Generative AI Adoption and AI Skill Demand (2023–2025)',
        fontsize=17,
        fontweight='bold',
        y=0.99,
    )

    _plot_indeed_trend(axes[0, 0], analysis.monthly)
    _plot_occupation(axes[0, 1], analysis.occupation)
    _plot_stackoverflow(axes[1, 0], analysis.monthly)
    _plot_country(axes[1, 1], analysis.country_2025)
    _plot_pct_change(axes[2, 0], analysis.monthly)
    _plot_decomposition(axes[2, 1], analysis.monthly, analysis.decomposition)

    axes[0, 0].set_title('1. Indeed job-share trend — raw vs. smoothed')
    axes[0, 1].set_title('2. Occupation comparison — relative demand by role')
    axes[1, 0].set_title('3. Stack Overflow usage — raw vs. smoothed')
    axes[1, 1].set_title('4. Country comparison — 2025 hiring index')
    axes[2, 0].set_title('5. Month-over-month change — direction and volatility')

    for ax in axes.flat:
        if ax not in (axes[2, 1],):
            ax.tick_params(axis='x', labelrotation=25)
    sns.despine(fig=fig)
    fig.text(
        0.01,
        0.005,
        'Source links and methods: see 06_REPORT.md. Monthly averages are descriptive.',
        fontsize=9,
        color='gray',
    )
    fig.tight_layout(pad=2.0, rect=[0, 0.02, 1, 0.96])
    fig.savefig(output_image_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f'[성공] 대시보드 이미지 저장: {output_image_path}')


def create_analysis_pdf(data_path, output_pdf_path):
    _configure_plot_style()
    analysis = prepare_data(data_path)
    monthly = analysis.monthly

    with PdfPages(output_pdf_path) as pdf:
        page_specs = (
            ('Indeed AI Job Share Trend (%)', lambda ax: _plot_indeed_trend(ax, monthly)),
            ('AI Skill Demand by Occupation (%)', lambda ax: _plot_occupation(ax, analysis.occupation)),
            ('Stack Overflow Developer AI Tool Usage (%)', lambda ax: _plot_stackoverflow(ax, monthly)),
            ('LinkedIn AI Hiring Index by Country (2025)', lambda ax: _plot_country(ax, analysis.country_2025)),
            ('Month-over-Month Change in Indeed AI Job Share (%)', lambda ax: _plot_pct_change(ax, monthly)),
        )
        for title, draw in page_specs:
            fig, ax = plt.subplots(figsize=(11, 8.5))
            draw(ax)
            ax.set_title(title, fontsize=14, fontweight='bold')
            ax.tick_params(axis='x', labelrotation=25)
            fig.tight_layout()
            pdf.savefig(fig)
            plt.close(fig)

        fig, axes = plt.subplots(3, 1, figsize=(11, 8.5), sharex=True)
        decomposition = analysis.decomposition
        axes[0].plot(monthly['datetime'], decomposition['observed'], label='Observed', alpha=0.65)
        axes[0].plot(monthly['datetime'], decomposition['trend'], label='Centered 2x12 moving average', linewidth=2)
        axes[0].set_title('Trend and observed series')
        axes[0].set_ylabel('Share (%)')
        axes[0].legend()
        axes[1].plot(monthly['datetime'], decomposition['seasonal'], color='#f59e0b')
        axes[1].set_title('Seasonal component (additive share points)')
        axes[1].set_ylabel('Share points')
        axes[2].plot(monthly['datetime'], decomposition['residual'], color='#dc2626')
        axes[2].axhline(0, color='#6b7280', linewidth=1)
        axes[2].set_title('Residual component')
        axes[2].set_ylabel('Share points')
        axes[2].tick_params(axis='x', labelrotation=25)
        fig.suptitle('6. Classical Additive Decomposition: Indeed AI Job Share')
        fig.tight_layout(rect=[0, 0, 1, 0.96])
        pdf.savefig(fig)
        plt.close(fig)

    print(f'[성공] 6페이지 PDF 리포트 저장: {output_pdf_path}')


def create_analysis_report(data_path, output_image_path, output_pdf_path, report_path):
    analysis = prepare_data(data_path)
    records = analysis.records
    monthly = analysis.monthly.set_index('datetime')
    quality = data_quality_summary(records)
    start = monthly['source_indeed_ai_job_share'].dropna().iloc[0]
    end = monthly['source_indeed_ai_job_share'].dropna().iloc[-1]
    overall_change = (end / start - 1) * 100
    periods = monthly['source_indeed_ai_job_share']
    first_half = periods.loc['2023-01':'2024-06'].mean()
    second_half = periods.loc['2024-07':'2025-12'].mean()
    annual_means = periods.resample('YS').mean()
    quarterly_means = periods.resample('QS').mean()
    observed_interval = periods.quantile([0.025, 0.975])
    sample = records[
        ['year_month', *METRIC_COLUMNS]
    ].head(10).to_string(index=False)
    missing_total = sum(item['missing_count'] for item in quality)
    outlier_total = sum(item['outlier_count'] for item in quality)
    quality_rows = '\n'.join(
        f"| `{item['column']}` | {item['missing_count']} | {item['outlier_count']} "
        f"| {item['lower_bound']:.3f}–{item['upper_bound']:.3f} |"
        for item in quality
    )
    annual_rows = '\n'.join(
        f'| {date.year} | {value:.3f} |'
        for date, value in annual_means.items()
    )
    quarterly_rows = '\n'.join(
        f'| {date:%Y-%m} | {value:.3f} |'
        for date, value in quarterly_means.items()
    )
    generated_at = datetime.now().astimezone().isoformat(timespec='seconds')
    with Image.open(output_image_path) as image:
        image_width, image_height = image.size
    image_name = os.path.relpath(output_image_path, os.path.dirname(report_path)).replace(os.sep, '/')
    pdf_name = os.path.relpath(output_pdf_path, os.path.dirname(report_path)).replace(os.sep, '/')

    content = f"""# AI Trend Analysis Report

> 생성 시각: {generated_at}
> GitHub: https://github.com/bigpark61/data_trend
> 데이터 원문: [Indeed Hiring Lab](https://www.hiringlab.org/) · [Stack Overflow Survey](https://survey.stackoverflow.co/2024/ai) · [LinkedIn Economic Graph](https://economicgraph.linkedin.com/)
> 데이터 파일: `ai_trend_dataset_template.csv` ({len(records):,}행, {monthly.shape[0]}개월, {records['datetime'].min():%Y-%m}–{records['datetime'].max():%Y-%m})

## 1. 분석 목적과 질문별 지표

| 분석 질문 | 사용 지표와 산식 |
|---|---|
| AI 채용공고 비중은 기간 중 어떻게 달라졌는가? | `source_indeed_ai_job_share`: 월별 산술평균, 전월 대비 변화율 `(현재월/전월-1)×100`, 3개월 후행 이동평균 |
| 개발자의 AI 도구 사용률은 채용 수요와 같은 방향으로 움직였는가? | `source_so_ai_use_rate`와 Indeed 비중의 월별 평균·전월 대비 변화율을 각각 비교 (두 출처의 모집단·측정주기가 다르므로 인과관계로 해석하지 않음) |
| AI 채용 지수는 2025년에 국가별로 어떻게 달랐는가? | `source_linkedin_ai_hiring_index`: 2025년 국가별 산술평균 (지수 기준 2023=100) |

## 2. 처리 단계와 재현 방법

| 단계 | 함수 | 입력 → 출력 |
|---|---|---|
| CSV 로드·검증 | `ai_trend_data.load_dataset` | CSV → 정규화된 컬럼명, 검증된 날짜·키·수치형 DataFrame |
| 월별/직무/국가 집계·파생변수 | `ai_trend_data.prepare_data` | DataFrame → 월별 평균, 3MA, 전월 변화율, 직무/국가 비교, 분해 성분 |
| PNG 대시보드 | `ai_trend_visual.create_ai_trend_dashboard` | CSV → `{image_name}` |
| PDF 생성 | `ai_trend_visual.create_analysis_pdf` | CSV → `{pdf_name}` (6페이지) |
| 보고서 생성 | `ai_trend_visual.create_analysis_report` | CSV 및 산출물 경로 → `06_REPORT.md` |
| 웹 API·대시보드 | `app.build_charts`, `GET /api/data`, `templates/index.html` | 동일 공통 집계 → JSON → Chart.js |

재생성: `python ai_trend_visual.py` (프로젝트 가상환경을 활성화한 경우). 그래프의 목적은 순서대로 추세 완화 비교, 직무 간 비교, 개발자 사용률 추세, 국가 간 비교, 전월 변화 방향·변동성, 추세·계절성·잔차의 분리입니다.

## 3. 원본 CSV 샘플

아래는 원본에서 추출한 첫 10행 중 날짜와 핵심 지표입니다. 전체 레코드는 **{len(records):,}행**입니다.

```text
{sample}
```

## 4. 시계열 결과와 집계 민감도

| 분석 | 결과 |
|---|---|
| Indeed 시작월 → 종료월 | {start:.3f}% → {end:.3f}% ({end - start:+.3f}%p, 상대 변화 {overall_change:+.2f}%) |
| 전체 월별 관측치의 2.5–97.5 백분위 | {observed_interval.iloc[0]:.3f}%–{observed_interval.iloc[1]:.3f}% (관측 구간이며 신뢰구간이 아님) |
| 전반 18개월 평균 (2023-01–2024-06) | {first_half:.3f}% |
| 후반 18개월 평균 (2024-07–2025-12) | {second_half:.3f}% (전반 대비 {(second_half / first_half - 1) * 100:+.2f}%) |

### 대체 집계 단위: 분기 평균

월별 평균 36개를 분기별 산술평균으로 다시 묶었습니다. 월별 자료의 단기 변동은 감춰지므로 분기 집계는 장기 수준 비교에만 사용합니다.

| 분기 시작월 | Indeed AI job share 평균 (%) |
|---|---:|
{quarterly_rows}

### 기간 선택 반례: 연도별 평균

시작·종료월 비교는 일부 월의 영향을 받습니다. 연도별 평균으로 바꾸면 아래와 같아, 동일한 상승 방향이더라도 기간·집계 선택에 따라 크기가 달라집니다.

| 연도 | 월별 값의 연평균 (%) |
|---|---:|
{annual_rows}

## 5. 결측·이상치 규정

- `year_month`의 `%b-%y` 파싱 실패, 국가/직무 키 결측·빈 값, 날짜·국가·직무 조합 중복, 숫자 칼럼의 비결측 문자열은 분석을 중단하고 오류를 냅니다. 줄바꿈·공백이 포함된 CSV 헤더는 공백 제거 후 매핑합니다.
- 수치 지표의 결측은 대체하거나 행 삭제하지 않습니다. 월별 평균은 존재하는 관측치로 계산하고, 해당 월의 모든 값이 결측이면 결과도 결측으로 유지합니다. 연속 3개월 이동평균은 결측을 메우지 않으며 유효값이 1개 이상인 창에서만 계산합니다.
- 이상치는 각 수치 칼럼 전체에서 Tukey 기준 `Q1−1.5×IQR` 미만 또는 `Q3+1.5×IQR` 초과로 **표시만** 합니다. 원값을 제거·대체하지 않습니다. 이 기준은 오류 판정이 아니라 검토 신호이며, 분포 꼬리의 실제 관측치일 수 있습니다.

| 수치 칼럼 | 결측 행 | IQR 표시 행 | 표시 기준 하한–상한 |
|---|---:|---:|---:|
{quality_rows}

검사 결과: 수치 지표 전체 결측 **{missing_total}건**, IQR 표시 **{outlier_total}건**. 어떤 값도 결측 대체나 이상치 제거로 바꾸지 않았습니다.

## 6. 시각화 산출물

![6개 패널 대시보드: 추세, 직무·국가 비교, 전월 변화율 및 계절 분해]({image_name})

**그림 1.** 6패널 PNG 대시보드 (`{image_name}`), {image_width}×{image_height}픽셀, 150 dpi. 패널은 추세/평활 비교, 직무 비교, 사용자 추세, 국가 비교, 전월 변화율, Indeed 가법 분해를 보여줍니다.

**부록 PDF:** [`{pdf_name}`]({pdf_name}), US Letter 가로형(11×8.5인치) 기준 6페이지: Indeed 추세, 직무 비교, Stack Overflow 사용률, 2025 국가 비교, 전월 변화율, 가법 분해.

## 7. 해석, 불확실성 및 한계

- 변화율은 월별 집계값의 단순 전월 대비 비율입니다. 분모가 작을 때 크게 흔들리고 기준월의 영향을 받습니다. 첫 달은 이전 월이 없어 정의되지 않습니다.
- 3MA는 후행 평활값으로 급격한 전환을 늦게 반영하고 시작 구간은 1–2개 관측치만으로 계산됩니다. 계절분해는 12개월 이동평균 두 개를 중심 정렬한 2×12 이동평균을 추세로 한 가법 분해이며 양 끝 6개월의 추세·잔차가 계산되지 않습니다. 36개월의 짧은 기간에서 계절 성분을 확정적 반복 주기로 일반화하지 않습니다.
- 월별 값은 기술통계이며 확률 표본 설계나 독립 관측 가정이 확인되지 않았습니다. 따라서 p-value와 모집단 신뢰구간을 계산하지 않았습니다. 2.5–97.5 백분위는 관측값 분포 요약일 뿐 불확실성 구간이 아닙니다.
- Stack Overflow 설문과 채용공고·LinkedIn 지수는 모집단, 수집 방식, 분모가 서로 다르고 표본 편향이 있을 수 있습니다. 동행은 인과를 뜻하지 않습니다. 비교 가능한 출처 정의·관측 시점 확인과 교차 검증이 필요합니다.

## 8. 권장 후속 액션과 KPI

AI 직무 수요가 높은 직군을 대상으로 8주 교육 파일럿을 제안합니다. **제안 KPI(관측된 결과가 아닌 목표):** 등록자의 80% 이상 수료, 사전 대비 사후 실무 평가점수 평균 10% 이상 향상. 수료율은 수료자/등록자로, 역량 변화는 동일 문항 사전·사후 평가의 개인별 점수 변화로 측정합니다. 한 개 파일럿에서 인과 효과가 입증됐다고 주장하지 말고 비교군·후속 채용 지표를 별도 수집합니다.

교차검증 후보: [U.S. Bureau of Labor Statistics Employment data](https://www.bls.gov/data/) 및 [Stanford AI Index](https://aiindex.stanford.edu/report/). 지표 정의·국가·기간의 호환성을 먼저 확인해야 하며 직접 합산하지 않습니다.

## 9. 출처 및 AI 사용 기록

| 출처 | 원문 |
|---|---|
| GitHub 저장소 | https://github.com/bigpark61/data_trend |
| Indeed Hiring Lab | https://www.hiringlab.org/ |
| Stack Overflow Developer Survey – AI | https://survey.stackoverflow.co/2024/ai |
| LinkedIn Economic Graph | https://economicgraph.linkedin.com/ |
| Stanford AI Index | https://aiindex.stanford.edu/report/ |

CSV에는 출처별 월별 값이 결합되어 있지만 원자료 추출 쿼리, 원문 파일/행과 각 값의 대응표는 저장소에 없습니다. 위 링크는 원문 출처 안내이며, 현 CSV의 각 행이 해당 사이트에서 직접 내려받은 관측치임을 증명하지 않습니다. 데이터 계보를 완전히 재현하려면 원자료 URL·추출일·변환 내역을 별도 보존해야 합니다.

AI 사용 로그: 기존 평가 전의 프롬프트·응답 전문과 타임스탬프는 저장소에 없어 복원할 수 없습니다. 이번 요청의 기록된 프롬프트는 “위 평가결과를 반영하여 프로그램을 보완해줘”이며, 정확한 대화 시각은 이 생성 스크립트에 제공되지 않았습니다. 이번 보완 응답 요약: CSV 입력 검증과 공통 집계를 추가하고, 월별 변화율·가법 계절분해·분기/기간 비교 및 차트/보고서 산출물을 구현했습니다. 이 요약은 원문 대화 로그가 아닙니다. 이 보고서의 생성 시각은 위에 별도로 기록됩니다. 검증은 `python -m unittest test_ai_trend_data.py` 및 `python ai_trend_visual.py`로 재현할 수 있고, 실행 결과는 저장된 실제 파일을 확인해야 합니다.
"""
    with open(report_path, 'w', encoding='utf-8') as report_file:
        report_file.write(content)


if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(base_dir, 'ai_trend_dataset_template.csv')
    output_dir = os.path.join(base_dir, 'output')
    os.makedirs(output_dir, exist_ok=True)

    output_image = os.path.join(output_dir, 'ai_trend_visualization.png')
    output_pdf = os.path.join(output_dir, 'ai_trend_analysis_6pages.pdf')
    report_file = os.path.join(base_dir, '06_REPORT.md')

    create_ai_trend_dashboard(data_file, output_image)
    create_analysis_pdf(data_file, output_pdf)
    create_analysis_report(data_file, output_image, output_pdf, report_file)
