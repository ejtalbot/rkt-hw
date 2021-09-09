"""Module for processing sample data"""
from datetime import datetime
from functools import lru_cache
from glob import glob
from os import path

import pandas as pd

from utils.mappings import BOROUGH_NAME_TO_INT_MAP


class SampleDataStore:
    """Class for cleaning sample data

    Attributes:
        sample_data_folder: folder with sample csv data
        df: DataFrame of all the csvs in the sample folder

    """

    def __init__(self, sample_data_folder: str):
        self.sample_data_folder = sample_data_folder
        self.df = pd.concat(
            map(pd.read_csv, glob(path.join(sample_data_folder, "sample_*.csv")))
        )

    def get_invalid_records(self) -> pd.DataFrame:
        """Runs some checks on the sample data to identify invalid rows

        Returns:
            DataFrame of the invalid rows

        """
        invalid_date_rows = self.df.loc[
            ~self.df["tstamp"].apply(lambda x: self.validate_date(x))
        ]
        invalid_critical_flag_rows = self.df.loc[
            ~self.df["critical_flag"].isin(
                ["Critical", "Not Critical", "Not Applicable"]
            )
        ]
        invalid_borough_rows = self.df.loc[
            ~self.df["borough"].isin(BOROUGH_NAME_TO_INT_MAP.keys())
        ]
        invalid_rows_df = pd.concat(
            [invalid_date_rows, invalid_critical_flag_rows, invalid_borough_rows]
        )
        invalid_rows_df.drop_duplicates(inplace=True)
        return invalid_rows_df

    def get_valid_records(self) -> pd.DataFrame:
        """Return DataFrame with valid records from sample csvs

        Returns:
            Pandas DataFrame with rows that passed validation

        """
        invalid_rows_df = self.get_invalid_records()
        merged_df = pd.merge(self.df, invalid_rows_df, how="outer", indicator=True)
        valid_rows_df = merged_df.loc[merged_df._merge == "left_only"]
        valid_rows_df.drop(columns="_merge", inplace=True)
        return valid_rows_df

    @staticmethod
    def validate_date(date_string: str) -> bool:
        """Validate if a input is a valid date string

        Args:
            date_string: string representation of a date

        Returns:
            True if the date is valid, False if it is not

        """
        try:
            datetime.strptime(date_string, "%Y-%m-%d")
            return True
        except (ValueError, TypeError):
            return False


@lru_cache(maxsize=None)
def get_sanitized_data(sample_data_folder: str) -> pd.DataFrame:
    """Create a DataFrame of sanitized data from a directory of csv samples

    Args:
        sample_data_folder: name of the folder for sample data to access

    Returns:
        A DataFrame of sanitized data

    """
    sample_data_store = SampleDataStore(sample_data_folder)
    return sample_data_store.get_valid_records()
