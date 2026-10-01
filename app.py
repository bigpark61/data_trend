from flask import Flask, jsonify, send_from_directory
import os
from math import isfinite

from ai_trend_data import prepare_data

app = Flask(__name__, static_folder='static')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, 'ai_trend_dataset_template.csv')


def _json_values(values):
    result = []
    for value in values:
        if value is None:
            result.append(None)
            continue
        numeric_value = float(value)
        result.append(round(numeric_value, 2) if isfinite(numeric_value) else None)
    return result


def build_charts():
    analysis = prepare_data(DATA_PATH)
    df_monthly = analysis.monthly
    df_occ = analysis.occupation
    df_country_2025 = analysis.country_2025
    decomposition = analysis.decomposition
    labels = df_monthly['datetime'].dt.strftime('%Y-%m').tolist()

    charts = [
        {
            'id': 'indeed-trend',
            'tabLabel': 'Indeed Trend',
            'title': 'Indeed AI Job Share Trend (%)',
            'type': 'line',
            'xAxisLabel': 'Date',
            'yAxisLabel': 'Share (%)',
            'labels': labels,
            'datasets': [
                {
                    'label': 'Monthly raw data',
                    'data': _json_values(df_monthly['source_indeed_ai_job_share']),
                    'borderColor': '#93c5fd',
                    'backgroundColor': 'rgba(147, 197, 253, 0.2)',
                    'fill': False,
                    'tension': 0.2
                },
                {
                    'label': '3-month moving average (3MA)',
                    'data': _json_values(df_monthly['ai_job_share_3ma']),
                    'borderColor': '#2563eb',
                    'backgroundColor': 'rgba(37, 99, 235, 0.2)',
                    'fill': False,
                    'tension': 0.2
                }
            ],
            'table': {
                'headers': ['Date', 'Monthly raw data', '3-month moving average (3MA)'],
                'rows': [
                    [date, raw, ma]
                    for date, raw, ma in zip(
                        df_monthly['datetime'].dt.strftime('%Y-%m'),
                        _json_values(df_monthly['source_indeed_ai_job_share']),
                        _json_values(df_monthly['ai_job_share_3ma'])
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
                    'data': _json_values(df_occ[col]),
                    'borderColor': f'rgba({idx * 40 + 50}, {90 + idx * 20}, {180 - idx * 20}, 1)',
                    'fill': False,
                    'tension': 0.2
                }
                for idx, col in enumerate(df_occ.columns)
            ],
            'table': {
                'headers': ['Date'] + list(df_occ.columns),
                'rows': [
                    [date] + _json_values(row)
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
            'labels': labels,
            'datasets': [
                {
                    'label': 'Monthly usage rate',
                    'data': _json_values(df_monthly['source_so_ai_use_rate']),
                    'borderColor': '#f87171',
                    'backgroundColor': 'rgba(248, 113, 113, 0.2)',
                    'fill': False,
                    'tension': 0.2
                },
                {
                    'label': '3-month moving average (3MA)',
                    'data': _json_values(df_monthly['so_ai_use_rate_3ma']),
                    'borderColor': '#dc2626',
                    'backgroundColor': 'rgba(220, 38, 38, 0.2)',
                    'fill': False,
                    'tension': 0.2
                }
            ],
            'table': {
                'headers': ['Date', 'Monthly usage rate', '3-month moving average (3MA)'],
                'rows': [
                    [date, raw, ma]
                    for date, raw, ma in zip(
                        df_monthly['datetime'].dt.strftime('%Y-%m'),
                        _json_values(df_monthly['source_so_ai_use_rate']),
                        _json_values(df_monthly['so_ai_use_rate_3ma'])
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
                    'data': _json_values(df_country_2025.values),
                    'backgroundColor': ['#dbeafe', '#bfdbfe', '#93c5fd', '#60a5fa', '#3b82f6'],
                    'borderWidth': 1
                }
            ],
            'table': {
                'headers': ['Country', 'AI Hiring Index'],
                'rows': [
                    [country, value]
                    for country, value in zip(df_country_2025.index, df_country_2025.values)
                ]
            }
        },
        {
            'id': 'indeed-change',
            'tabLabel': 'Monthly Change',
            'title': 'Indeed AI Job Share Month-over-Month Change (%)',
            'type': 'line',
            'xAxisLabel': 'Date',
            'yAxisLabel': 'Change (%)',
            'labels': labels,
            'datasets': [{
                'label': 'Monthly change (%)',
                'data': _json_values(df_monthly['ai_job_share_pct_change']),
                'borderColor': '#7c3aed',
                'fill': False,
                'spanGaps': False,
            }],
            'table': {
                'headers': ['Date', 'Monthly change (%)'],
                'rows': [
                    [date, change]
                    for date, change in zip(
                        labels,
                        _json_values(df_monthly['ai_job_share_pct_change']),
                    )
                ]
            }
        },
        {
            'id': 'decomposition',
            'tabLabel': 'Decomposition',
            'title': 'Indeed AI Job Share Additive Decomposition',
            'type': 'line',
            'xAxisLabel': 'Date',
            'yAxisLabel': 'Share / share points',
            'labels': labels,
            'datasets': [
                {
                    'label': component.title(),
                    'data': _json_values(decomposition[component]),
                    'borderColor': color,
                    'fill': False,
                    'spanGaps': False,
                }
                for component, color in (
                    ('observed', '#93c5fd'),
                    ('trend', '#1d4ed8'),
                    ('seasonal', '#f59e0b'),
                    ('residual', '#dc2626'),
                )
            ],
            'table': {
                'headers': ['Date', 'Observed', 'Trend', 'Seasonal', 'Residual'],
                'rows': [
                    [date, *values]
                    for date, values in zip(
                        labels,
                        zip(*[
                            _json_values(decomposition[component])
                            for component in ('observed', 'trend', 'seasonal', 'residual')
                        ]),
                    )
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
