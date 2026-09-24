from flask import Flask, jsonify, send_from_directory
import pandas as pd
import os

app = Flask(__name__, static_folder='static')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, 'ai_trend_dataset_template.csv')


def load_dataframe():
    df = pd.read_csv(DATA_PATH)
    df['datetime'] = pd.to_datetime(df['year_month'])
    return df


def build_charts():
    df = load_dataframe()

    df_monthly = df.groupby('datetime')[[
        'source_indeed_ai_job_share',
        'source_so_ai_use_rate',
        'source_linkedin_ai_hiring_index'
    ]].mean().reset_index()
    df_monthly['ai_job_share_3ma'] = df_monthly['source_indeed_ai_job_share'].rolling(window=3, min_periods=1).mean()
    df_monthly['so_ai_use_rate_3ma'] = df_monthly['source_so_ai_use_rate'].rolling(window=3, min_periods=1).mean()

    df_occ = df.groupby(['datetime', 'occupation'])['source_indeed_ai_job_share'].mean().unstack()
    df_country_2025 = df[df['year_month'].str.startswith('2025')].groupby('country')['source_linkedin_ai_hiring_index'].mean().sort_values(ascending=False)

    charts = [
        {
            'id': 'indeed-trend',
            'tabLabel': 'Indeed Trend',
            'title': 'Indeed AI Job Share Trend (%)',
            'type': 'line',
            'xAxisLabel': 'Date',
            'yAxisLabel': 'Share (%)',
            'labels': df_monthly['datetime'].dt.strftime('%Y-%m').tolist(),
            'datasets': [
                {
                    'label': 'Monthly raw data',
                    'data': df_monthly['source_indeed_ai_job_share'].tolist(),
                    'borderColor': '#93c5fd',
                    'backgroundColor': 'rgba(147, 197, 253, 0.2)',
                    'fill': False,
                    'tension': 0.2
                },
                {
                    'label': '3-month moving average (3MA)',
                    'data': df_monthly['ai_job_share_3ma'].tolist(),
                    'borderColor': '#2563eb',
                    'backgroundColor': 'rgba(37, 99, 235, 0.2)',
                    'fill': False,
                    'tension': 0.2
                }
            ],
            'table': {
                'headers': ['Date', 'Monthly raw data', '3-month moving average (3MA)'],
                'rows': [
                    [date, round(raw, 2), round(ma, 2)]
                    for date, raw, ma in zip(
                        df_monthly['datetime'].dt.strftime('%Y-%m'),
                        df_monthly['source_indeed_ai_job_share'],
                        df_monthly['ai_job_share_3ma']
                    )
                ]
            }
        },
        {
            'id': 'occupation',
            'tabLabel': 'Occupation',
            'title': 'AI Skill Demand by Occupation (%)',
            'type': 'line',
            'xAxisLabel': 'Date',
            'yAxisLabel': 'Share (%)',
            'labels': df_occ.index.strftime('%Y-%m').tolist(),
            'datasets': [
                {
                    'label': col,
                    'data': df_occ[col].tolist(),
                    'borderColor': f'rgba({idx * 40 + 50}, {90 + idx * 20}, {180 - idx * 20}, 1)',
                    'fill': False,
                    'tension': 0.2
                }
                for idx, col in enumerate(df_occ.columns)
            ],
            'table': {
                'headers': ['Date'] + list(df_occ.columns),
                'rows': [
                    [date] + [round(value, 2) for value in row]
                    for date, row in zip(df_occ.index.strftime('%Y-%m'), df_occ.to_numpy())
                ]
            }
        },
        {
            'id': 'stackoverflow',
            'tabLabel': 'Stack Overflow',
            'title': 'Stack Overflow Developer AI Tool Usage Trend (%)',
            'type': 'line',
            'xAxisLabel': 'Date',
            'yAxisLabel': 'Usage rate (%)',
            'labels': df_monthly['datetime'].dt.strftime('%Y-%m').tolist(),
            'datasets': [
                {
                    'label': 'Monthly usage rate',
                    'data': df_monthly['source_so_ai_use_rate'].tolist(),
                    'borderColor': '#f87171',
                    'backgroundColor': 'rgba(248, 113, 113, 0.2)',
                    'fill': False,
                    'tension': 0.2
                },
                {
                    'label': '3-month moving average (3MA)',
                    'data': df_monthly['so_ai_use_rate_3ma'].tolist(),
                    'borderColor': '#dc2626',
                    'backgroundColor': 'rgba(220, 38, 38, 0.2)',
                    'fill': False,
                    'tension': 0.2
                }
            ],
            'table': {
                'headers': ['Date', 'Monthly usage rate', '3-month moving average (3MA)'],
                'rows': [
                    [date, round(raw, 2), round(ma, 2)]
                    for date, raw, ma in zip(
                        df_monthly['datetime'].dt.strftime('%Y-%m'),
                        df_monthly['source_so_ai_use_rate'],
                        df_monthly['so_ai_use_rate_3ma']
                    )
                ]
            }
        },
        {
            'id': 'country',
            'tabLabel': 'Country',
            'title': 'LinkedIn AI Hiring Index by Major Country (2025)',
            'type': 'bar',
            'xAxisLabel': 'Country',
            'yAxisLabel': 'AI Hiring Index (2023=100)',
            'labels': df_country_2025.index.tolist(),
            'datasets': [
                {
                    'label': 'AI Hiring Index',
                    'data': df_country_2025.values.tolist(),
                    'backgroundColor': ['#dbeafe', '#bfdbfe', '#93c5fd', '#60a5fa', '#3b82f6'],
                    'borderWidth': 1
                }
            ],
            'table': {
                'headers': ['Country', 'AI Hiring Index'],
                'rows': [
                    [country, round(value, 2)]
                    for country, value in zip(df_country_2025.index, df_country_2025.values)
                ]
            }
        }
    ]

    return {'charts': charts}


@app.route('/')
def index():
    return send_from_directory('templates', 'index.html')


@app.route('/api/data')
def data_api():
    return jsonify(build_charts())


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
