from typing import NamedTuple

import numpy as np
import pandas as pd


METRIC_COLUMNS = (
    'source_indeed_ai_job_share',
    'source_so_ai_use_rate',
    'source_linkedin_ai_hiring_index',
)
NUMERIC_COLUMNS = (
    'source_indeed_total_it_index',
    'source_indeed_ai_job_share',
    'source_so_ai_use_rate',
    'source_so_avg_salary_usd',
    'source_linkedin_ai_hiring_index',
    'source_stanford_genai_demand_score',
)
REQUIRED_COLUMNS = (
    'year_month',
    'country',
    'occupation',
    *NUMERIC_COLUMNS,
)


class AnalysisData(NamedTuple):
    records: pd.DataFrame
    monthly: pd.DataFrame
    occupation: pd.DataFrame
    country_2025: pd.Series
    decomposition: pd.DataFrame


def load_dataset(data_path):
    df = pd.read_csv(data_path)
    normalized_columns = [''.join(str(column).split()) for column in df.columns]
    if len(normalized_columns) != len(set(normalized_columns)):
        raise ValueError('공백 제거 후 중복되는 CSV 헤더가 있습니다.')
    df.columns = normalized_columns

    missing_columns = sorted(set(REQUIRED_COLUMNS) - set(df.columns))
    if missing_columns:
        raise ValueError(f'필수 CSV 컬럼이 없습니다: {", ".join(missing_columns)}')

    dates = pd.to_datetime(df['year_month'], format='%b-%y', errors='coerce')
    if dates.isna().any():
        invalid_count = int(dates.isna().sum())
        raise ValueError(f'year_month 날짜 형식이 올바르지 않은 행이 {invalid_count}개 있습니다.')
    df['datetime'] = dates

    for column in ('country', 'occupation'):
        if df[column].isna().any() or df[column].astype(str).str.strip().eq('').any():
            raise ValueError(f'{column} 식별자에 결측 또는 빈 값이 있습니다.')

    duplicate_count = int(df.duplicated(['datetime', 'country', 'occupation']).sum())
    if duplicate_count:
        raise ValueError(f'datetime/country/occupation 조합이 중복된 행이 {duplicate_count}개 있습니다.')

    for column in NUMERIC_COLUMNS:
        raw_values = df[column]
        numeric_values = pd.to_numeric(raw_values, errors='coerce')
        invalid_values = raw_values.notna() & numeric_values.isna()
        if invalid_values.any():
            raise ValueError(f'{column}에 숫자가 아닌 값이 {int(invalid_values.sum())}개 있습니다.')
        if not np.isfinite(numeric_values.dropna().to_numpy(dtype='float64')).all():
            raise ValueError(f'{column}에 유한하지 않은 숫자 값이 있습니다.')
        df[column] = numeric_values

    return df


def decompose_monthly_series(series, period=12):
    if len(series) < period * 2:
        raise ValueError(f'계절분해에는 최소 {period * 2}개월의 데이터가 필요합니다.')

    moving_average = series.rolling(window=period, min_periods=period).mean()
    trend = (
        (moving_average + moving_average.shift(1))
        .div(2)
        .shift(-(period // 2))
    )
    detrended = series - trend
    seasonal_by_month = detrended.groupby(detrended.index.month).mean()
    seasonal_by_month = seasonal_by_month - seasonal_by_month.mean()
    seasonal = pd.Series(
        [seasonal_by_month.get(month, np.nan) for month in series.index.month],
        index=series.index,
        dtype='float64',
    )

    return pd.DataFrame({
        'observed': series,
        'trend': trend,
        'seasonal': seasonal,
        'residual': series - trend - seasonal,
    })


def prepare_data(data_path):
    df = load_dataset(data_path)
    df_monthly = df.groupby('datetime')[list(METRIC_COLUMNS)].mean().sort_index()
    full_month_index = pd.date_range(
        df_monthly.index.min(),
        df_monthly.index.max(),
        freq='MS',
    )
    df_monthly = df_monthly.reindex(full_month_index)
    df_monthly.index.name = 'datetime'
    df_monthly = df_monthly.reset_index()

    df_monthly['ai_job_share_3ma'] = (
        df_monthly['source_indeed_ai_job_share'].rolling(window=3, min_periods=1).mean()
    )
    df_monthly['so_ai_use_rate_3ma'] = (
        df_monthly['source_so_ai_use_rate'].rolling(window=3, min_periods=1).mean()
    )
    df_monthly['ai_job_share_pct_change'] = (
        df_monthly['source_indeed_ai_job_share'].pct_change(fill_method=None) * 100
    )
    df_monthly['so_ai_use_rate_pct_change'] = (
        df_monthly['source_so_ai_use_rate'].pct_change(fill_method=None) * 100
    )

    df_occ = (
        df.groupby(['datetime', 'occupation'])['source_indeed_ai_job_share']
        .mean()
        .unstack()
        .sort_index()
    )
    df_country_2025 = (
        df[df['datetime'].dt.year.eq(2025)]
        .groupby('country')['source_linkedin_ai_hiring_index']
        .mean()
        .sort_values(ascending=False)
    )
    decomposition = decompose_monthly_series(
        df_monthly.set_index('datetime')['source_indeed_ai_job_share']
    )

    return AnalysisData(df, df_monthly, df_occ, df_country_2025, decomposition)


def data_quality_summary(df):
    summary = []
    for column in NUMERIC_COLUMNS:
        values = df[column]
        non_missing = values.dropna()
        if non_missing.empty:
            lower_bound = np.nan
            upper_bound = np.nan
            outlier_count = 0
        else:
            q1 = non_missing.quantile(0.25)
            q3 = non_missing.quantile(0.75)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            outlier_count = int(((values < lower_bound) | (values > upper_bound)).sum())
        summary.append({
            'column': column,
            'missing_count': int(values.isna().sum()),
            'outlier_count': outlier_count,
            'lower_bound': lower_bound,
            'upper_bound': upper_bound,
        })
    return summary
