from unittest import TestCase

import pandas as pd
import pytest

from utils.data_validation import SampleDataStore

class TestSampleDataStore(TestCase):
    def setUp(self):
        self.maxDiff = None
        self.sample_data_store = SampleDataStore("tests/utils/samples_example")

    def test_get_invalid_records(self):
        expected = pd.DataFrame(
            {
                "tstamp": [
                    "2020-99-99",
                    "2020-01-22",
                    "2020-01-31",
                ],
                "cuisine": [
                    "Asian",
                    "Pizza",
                    "Pizza",
                ],
                "critical_flag": [
                    "Critical",
                    "Not Criticaaal",
                    "Not Critical",
                ],
                "borough": ["Bronx", "Brooklyn", "Kings",],
            }
        )
        actual = self.sample_data_store.get_invalid_records()
        pd.testing.assert_frame_equal(actual.reset_index(drop=True), expected.reset_index(drop=True))

    def test_get_valid_records(self):
        expected = pd.DataFrame(
            {
                "tstamp": [
                    "2020-02-14",
                    "2020-02-14",
                    "2020-02-01",
                ],
                "cuisine": [
                    "American",
                    "Coffee/Tea",
                    "Mediterranean",
                ],
                "critical_flag": [
                    "Not Critical",
                    "Critical",
                    "Critical",
                ],
                "borough": ["Queens", "Queens", "Manhattan",]
            }
        )
        actual = self.sample_data_store.get_valid_records()
        pd.testing.assert_frame_equal(actual.reset_index(drop=True), expected.reset_index(drop=True))

    def test_validate_date_pass(self):
        expected = True
        actual = self.sample_data_store.validate_date('2020-01-01')
        self.assertEqual(actual, expected)

    def test_validate_date_fail(self):
        expected = False
        actual = self.sample_data_store.validate_date('2020-99-99')
        self.assertEqual(actual, expected)
