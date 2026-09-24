import matplotlib
matplotlib.use('Agg')  # Headless 환경 설정
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import seaborn as sns
import pandas as pd
import numpy as np
import os


def _prepare_data(data_path):
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"데이터 파일을 찾을 수 없습니다: {data_path}")

    df = pd.read_csv(data_path)
    df['datetime'] = pd.to_datetime(df['year_month'])

    df_monthly = df.groupby('datetime')[[
        'source_indeed_ai_job_share',
        'source_so_ai_use_rate',
        'source_linkedin_ai_hiring_index'
    ]].mean().reset_index()

    df_monthly['ai_job_share_3ma'] = df_monthly['source_indeed_ai_job_share'].rolling(window=3, min_periods=1).mean()
    df_monthly['so_ai_use_rate_3ma'] = df_monthly['source_so_ai_use_rate'].rolling(window=3, min_periods=1).mean()

    df_occ = df.groupby(['datetime', 'occupation'])['source_indeed_ai_job_share'].mean().unstack()
    df_country_2025 = df[df['year_month'].str.startswith('2025')].groupby('country')['source_linkedin_ai_hiring_index'].mean().sort_values(ascending=False)

    return df_monthly, df_occ, df_country_2025


def create_ai_trend_dashboard(data_path, output_image_path):
    # 1. Font and style configuration
    plt.rcParams['font.family'] = 'DejaVu Sans'
    plt.rcParams['axes.unicode_minus'] = False
    sns.set_theme(style='whitegrid', font='DejaVu Sans', palette='colorblind')

    df_monthly, df_occ, df_country_2025 = _prepare_data(data_path)

    fig, axes = plt.subplots(2, 2, figsize=(15, 11))
    fig.suptitle('Generative AI Adoption and Rising AI Skill Demand in Global IT Labor Markets (2023–2025)', fontsize=16, fontweight='bold', y=0.98)

    ax1 = axes[0, 0]
    ax1.plot(df_monthly['datetime'], df_monthly['source_indeed_ai_job_share'], color='#93c5fd', linestyle='--', alpha=0.7, label='Monthly raw data')
    ax1.plot(df_monthly['datetime'], df_monthly['ai_job_share_3ma'], color='#2563eb', linewidth=2.5, label='3-month moving average (3MA)')
    ax1.set_title('1. Indeed AI Job Share Trend (%)', fontsize=12, fontweight='bold', pad=10)
    ax1.set_ylabel('Share (%)')
    ax1.legend(loc='upper left', frameon=True)
    ax1.set_ylim(6.5, 9.5)

    ax2 = axes[0, 1]
    for occ in df_occ.columns:
        ax2.plot(df_occ.index, df_occ[occ], label=occ, linewidth=2)
    ax2.set_title('2. AI Skill Demand by Occupation (%)', fontsize=12, fontweight='bold', pad=10)
    ax2.set_ylabel('Share (%)')
    ax2.legend(loc='upper left', frameon=True, fontsize=9)

    ax3 = axes[1, 0]
    ax3.plot(df_monthly['datetime'], df_monthly['source_so_ai_use_rate'], color='#f87171', linestyle='--', alpha=0.7, label='Monthly usage rate')
    ax3.plot(df_monthly['datetime'], df_monthly['so_ai_use_rate_3ma'], color='#dc2626', linewidth=2.5, label='3-month moving average (3MA)')
    ax3.set_title('3. Stack Overflow Developer AI Tool Usage Trend (%)', fontsize=12, fontweight='bold', pad=10)
    ax3.set_ylabel('Usage rate (%)')
    ax3.legend(loc='lower left', frameon=True)

    ax4 = axes[1, 1]
    bars = ax4.bar(df_country_2025.index, df_country_2025.values, color=sns.color_palette('Blues_r', len(df_country_2025)))
    ax4.set_title('4. LinkedIn AI Hiring Index by Major Country (2025)', fontsize=12, fontweight='bold', pad=10)
    ax4.set_ylabel('AI Hiring Index (2023=100)')
    ax4.set_ylim(100, 145)

    for bar in bars:
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height + 0.8, f'{height:.1f}', ha='center', va='bottom', fontsize=9, fontweight='bold')

    sns.despine(fig=fig)
    plt.tight_layout(pad=2.0, rect=[0, 0.02, 1, 0.95])
    fig.text(0.01, 0.01, 'Source: Indeed Hiring Lab, Stack Overflow Developer Survey, LinkedIn Economic Graph (2023–2025 combined dataset)', fontsize=9, color='gray')

    plt.savefig(output_image_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"[성공] 대시보드 시각화 이미지가 성공적으로 저장되었습니다: {output_image_path}")


def create_four_page_report(data_path, output_pdf_path):
    plt.rcParams['font.family'] = 'DejaVu Sans'
    plt.rcParams['axes.unicode_minus'] = False
    sns.set_theme(style='whitegrid', font='DejaVu Sans', palette='colorblind')

    df_monthly, df_occ, df_country_2025 = _prepare_data(data_path)

    with PdfPages(output_pdf_path) as pdf:
        # Page 1: Indeed trend
        fig1, ax1 = plt.subplots(figsize=(11, 8.5))
        ax1.plot(df_monthly['datetime'], df_monthly['source_indeed_ai_job_share'], color='#93c5fd', linestyle='--', alpha=0.7, label='Monthly raw data')
        ax1.plot(df_monthly['datetime'], df_monthly['ai_job_share_3ma'], color='#2563eb', linewidth=2.5, label='3-month moving average (3MA)')
        ax1.set_title('1. Indeed AI Job Share Trend (%)', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Share (%)')
        ax1.legend(loc='upper left', frameon=True)
        ax1.set_ylim(6.5, 9.5)
        fig1.tight_layout()
        pdf.savefig(fig1)
        plt.close(fig1)

        # Page 2: Occupation comparison
        fig2, ax2 = plt.subplots(figsize=(11, 8.5))
        for occ in df_occ.columns:
            ax2.plot(df_occ.index, df_occ[occ], label=occ, linewidth=2)
        ax2.set_title('2. AI Skill Demand by Occupation (%)', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Share (%)')
        ax2.legend(loc='upper left', frameon=True, fontsize=9)
        fig2.tight_layout()
        pdf.savefig(fig2)
        plt.close(fig2)

        # Page 3: Stack Overflow usage
        fig3, ax3 = plt.subplots(figsize=(11, 8.5))
        ax3.plot(df_monthly['datetime'], df_monthly['source_so_ai_use_rate'], color='#f87171', linestyle='--', alpha=0.7, label='Monthly usage rate')
        ax3.plot(df_monthly['datetime'], df_monthly['so_ai_use_rate_3ma'], color='#dc2626', linewidth=2.5, label='3-month moving average (3MA)')
        ax3.set_title('3. Stack Overflow Developer AI Tool Usage Trend (%)', fontsize=14, fontweight='bold')
        ax3.set_ylabel('Usage rate (%)')
        ax3.legend(loc='lower left', frameon=True)
        fig3.tight_layout()
        pdf.savefig(fig3)
        plt.close(fig3)

        # Page 4: Country ranking
        fig4, ax4 = plt.subplots(figsize=(11, 8.5))
        bars = ax4.bar(df_country_2025.index, df_country_2025.values, color=sns.color_palette('Blues_r', len(df_country_2025)))
        ax4.set_title('4. LinkedIn AI Hiring Index by Major Country (2025)', fontsize=14, fontweight='bold')
        ax4.set_ylabel('AI Hiring Index (2023=100)')
        ax4.set_ylim(100, 145)
        for bar in bars:
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height + 0.8, f'{height:.1f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
        fig4.tight_layout()
        pdf.savefig(fig4)
        plt.close(fig4)

    print(f"[성공] 4페이지 PDF 리포트가 저장되었습니다: {output_pdf_path}")


if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(base_dir, 'ai_trend_dataset_template.csv')
    output_dir = os.path.join(base_dir, 'output')
    os.makedirs(output_dir, exist_ok=True)

    output_file = os.path.join(output_dir, 'ai_trend_visualization.png')
    output_pdf = os.path.join(output_dir, 'ai_trend_report_4pages.pdf')

    create_ai_trend_dashboard(data_file, output_file)
    create_four_page_report(data_file, output_pdf)
