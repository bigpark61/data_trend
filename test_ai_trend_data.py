import tempfile
import unittest
from pathlib import Path

import pandas as pd

from ai_trend_data import data_quality_summary, prepare_data


class PrepareDataTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.data_path = Path(self.temp_dir.name) / 'sample.csv'
        dates = pd.date_range('2023-01-01', periods=36, freq='MS')
        rows = []
        for date in dates:
            for country in ('A', 'B'):
                rows.append({
                    'year_month': date.strftime('%b-%y'),
                    'country': country,
                    'occupation': 'Engineer',
                    'source_indeed_total_it_index': 100,
                    'source_indeed_ai_job_share': 5 + date.month / 10,
                    'source_so_ai_use_rate': 60 + date.month,
                    'source_so_avg_salary_usd': 70000,
                    'source_linkedin_ai_hiring_index': 100 + date.month,
                    'source_stanford_genai_demand_score': 50 + date.month,
                })
        self.rows = rows

    def tearDown(self):
        self.temp_dir.cleanup()

    def write_csv(self):
        pd.DataFrame(self.rows).to_csv(self.data_path, index=False)

    def test_normalizes_split_headers_and_calculates_time_series(self):
        frame = pd.DataFrame(self.rows).rename(
            columns={'source_indeed_ai_job_share': 'source_indeed_\nai_job_share'}
        )
        frame.to_csv(self.data_path, index=False)

        analysis = prepare_data(self.data_path)

        self.assertEqual(len(analysis.records), 72)
        self.assertEqual(len(analysis.monthly), 36)
        self.assertTrue(pd.isna(analysis.monthly['ai_job_share_pct_change'].iloc[0]))
        self.assertAlmostEqual(
            analysis.monthly['ai_job_share_pct_change'].iloc[1],
            (5.2 / 5.1 - 1) * 100,
        )
        self.assertEqual(analysis.decomposition['trend'].notna().sum(), 24)
        valid = analysis.decomposition.dropna()
        self.assertTrue(
            (
                valid['observed']
                - valid['trend']
                - valid['seasonal']
                - valid['residual']
            ).abs().lt(1e-10).all()
        )

    def test_missing_measurements_are_not_imputed_or_removed(self):
        self.rows[0]['source_indeed_ai_job_share'] = None
        self.write_csv()

        analysis = prepare_data(self.data_path)
        quality = data_quality_summary(analysis.records)
        job_share = next(item for item in quality if item['column'] == 'source_indeed_ai_job_share')

        self.assertEqual(len(analysis.records), 72)
        self.assertEqual(job_share['missing_count'], 1)
        self.assertTrue(pd.notna(analysis.monthly['source_indeed_ai_job_share'].iloc[0]))

    def test_invalid_measurement_text_fails_explicitly(self):
        self.rows[0]['source_indeed_ai_job_share'] = 'not-a-number'
        self.write_csv()

        with self.assertRaisesRegex(ValueError, '숫자가 아닌 값'):
            prepare_data(self.data_path)

    def test_non_finite_measurement_fails_explicitly(self):
        self.rows[0]['source_indeed_ai_job_share'] = float('inf')
        self.write_csv()

        with self.assertRaisesRegex(ValueError, '유한하지 않은 숫자'):
            prepare_data(self.data_path)


if __name__ == '__main__':
    unittest.main()
