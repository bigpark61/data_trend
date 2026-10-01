
이전 단계에서 생성한 **`ai_trend_dataset_template.csv`** 통합 데이터셋을 활용하여 시계열 추세 및 이동평균선(3MA), 직무별/국가별 비교를 다각도로 분석하는 **Python 시각화 코드**를 구성했습니다.

생성된 시각화 결과물(`ai_trend_visualization.png`)과 파이썬 스크립트 파일(`ai_trend_visualization_script.py`)은 **스튜디오(Studio) 패널**에 탑재되어 있습니다.

---

### 데이터 시각화 파이썬 코드 (`ai_trend_visualization_script.py`)

이 코드는 **Seaborn**과 **Matplotlib**을 활용하여 4개의 핵심 지표를 한눈에 비교할 수 있는 2x2 대시보드로 구성되어 있습니다.

```
import matplotlib
matplotlib.use('Agg')  # Headless 환경 설정
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import os

def create_ai_trend_dashboard(data_path, output_image_path):
    # 1. 한글 폰트 및 스타일 설정
    plt.rcParams['font.family'] = 'Noto Sans CJK JP'  # 한글 지원 폰트
    plt.rcParams['axes.unicode_minus'] = False
    sns.set_theme(style='whitegrid', font='Noto Sans CJK JP', palette='colorblind')

    # 2. 데이터 로드 및 전처리
    df = pd.read_csv(data_path)
    df['datetime'] = pd.to_datetime(df['year_month'])

    # 월별 시계열 집계 및 3개월 이동평균(3MA) 산출
    df_monthly = df.groupby('datetime')[['source_indeed_ai_job_share',
                                         'source_so_ai_use_rate',
                                         'source_linkedin_ai_hiring_index']].mean().reset_index()

    df_monthly['ai_job_share_3ma'] = df_monthly['source_indeed_ai_job_share'].rolling(window=3, min_periods=1).mean()
    df_monthly['so_ai_use_rate_3ma'] = df_monthly['source_so_ai_use_rate'].rolling(window=3, min_periods=1).mean()

    # 직무별 및 국가별 데이터 집계
    df_occ = df.groupby(['datetime', 'occupation'])['source_indeed_ai_job_share'].mean().unstack()
    df_country_2025 = df[df['year_month'].str.startswith('2025')].groupby('country')['source_linkedin_ai_hiring_index'].mean().sort_values(ascending=False)

    # 3. 대시보드 피규어 생성 (2x2 대시보드)
    fig, axes = plt.subplots(2, 2, figsize=(15, 11))
    fig.suptitle('생성형 AI 확산에 따른 글로벌 IT 노동시장 AI 요구 비중 19.5% 증가 (2023~2025)',
                 fontsize=16, fontweight='bold', y=0.98)

    # [차트 1] Indeed AI 채용공고 비중 추이 (월별 원데이터 + 3MA 이동평균)
    ax1 = axes
    ax1.plot(df_monthly['datetime'], df_monthly['source_indeed_ai_job_share'], color='#93c5fd', linestyle='--', alpha=0.7, label='월별 원데이터')
    ax1.plot(df_monthly['datetime'], df_monthly['ai_job_share_3ma'], color='#2563eb', linewidth=2.5, label='3개월 이동평균(3MA)')
    ax1.set_title('1. Indeed AI 채용공고 비중 추이 (%)', fontsize=12, fontweight='bold', pad=10)
    ax1.set_ylabel('비중 (%)')
    ax1.legend(loc='upper left', frameon=True)
    ax1.set_ylim(6.5, 9.5)

    # [차트 2] 직무별 채용공고 내 AI 요구 비중 비교
    ax2 = axes
    for occ in df_occ.columns:
        ax2.plot(df_occ.index, df_occ[occ], label=occ, linewidth=2)
    ax2.set_title('2. 직무별 채용공고 내 AI 요구 비중 비교 (%)', fontsize=12, fontweight='bold', pad=10)
    ax2.set_ylabel('비중 (%)')
    ax2.legend(loc='upper left', frameon=True, fontsize=9)

    # [차트 3] Stack Overflow 개발자 AI 도구 활용률 추이
    ax3 = axes
    ax3.plot(df_monthly['datetime'], df_monthly['source_so_ai_use_rate'], color='#f87171', linestyle='--', alpha=0.7, label='월별 활용률')
    ax3.plot(df_monthly['datetime'], df_monthly['so_ai_use_rate_3ma'], color='#dc2626', linewidth=2.5, label='3개월 이동평균(3MA)')
    ax3.set_title('3. Stack Overflow 개발자 AI 도구 활용률 추이 (%)', fontsize=12, fontweight='bold', pad=10)
    ax3.set_ylabel('활용률 (%)')
    ax3.legend(loc='lower left', frameon=True)

    # [차트 4] 2025년 주요 국가별 LinkedIn AI 채용 지수
    ax4 = axes
    bars = ax4.bar(df_country_2025.index, df_country_2025.values, color=sns.color_palette('Blues_r', len(df_country_2025)))
    ax4.set_title('4. 2025년 주요 국가별 LinkedIn AI 채용 지수', fontsize=12, fontweight='bold', pad=10)
    ax4.set_ylabel('AI 채용 지수 (2023=100)')
    ax4.set_ylim(100, 145)

    # 바 그래프 상단에 데이터 라벨 표기
    for bar in bars:
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height + 0.8, f'{height:.1f}',
                 ha='center', va='bottom', fontsize=9, fontweight='bold')

    # 공통 레이아웃 정돈 및 출처 기재
    sns.despine(fig=fig)
    plt.tight_layout(pad=2.0, rect=[0, 0.02, 1, 0.95])
    fig.text(0.01, 0.01, 'Source: Indeed Hiring Lab, Stack Overflow Developer Survey, LinkedIn Economic Graph (2023-2025 통합 데이터셋)', fontsize=9, color='gray')

    # 이미지 저장
    plt.savefig(output_image_path, dpi=150, bbox_inches='tight')
    plt.close()

if __name__ == '__main__':
    data_file = 'ai_trend_dataset_template.csv'
    output_file = 'ai_trend_visualization.png'
    create_ai_trend_dashboard(data_file, output_file)
```

---

### 코드의 핵심 분석 기술 포인트

1. **시계열 노이즈 제거 (3MA)**: 가이드 문서의 지침에 따라 3개월 이동평균선(`rolling(window=3)`)을 적용하여 월별 단기 변동성을 제거하고 명확한 트렌드 경향을 가시화했습니다.
2. **다차원 데이터 비교**: `Indeed`(채용 수요), `Stack Overflow`(개발자 활용률), `LinkedIn`(국가별 채용 지수) 세 소스의 지표를 단일 대시보드 상에서 입체적으로 비교할 수 있습니다.
3. **결론 중심의 차트 타이틀 (Insight Title)**: 차트의 전체 구성을 대표하는 주 타이틀에 핵심 인사이트 수치(글로벌 AI 요구 비중 19.5% 증가)를 명시했습니다.

---

📊 **이 시각화 차트와 데이터 통계를 바탕으로 과제 보고서용 요약 분석서나 슬라이드 발표자료 형태로 정리해 볼까요?**