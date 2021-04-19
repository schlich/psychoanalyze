import os
from pathlib import Path
import pandas as pd
from hypothesis import given
from hypothesis.strategies import lists, text


def test_data_exists():
    assert os.path.isfile("data/data.h5")


def test_tables_in_hdf_keys():
    # csv_name_list = [file.stem for file in Path("data/csv").iterdir()]
    with pd.HDFStore("data/data.h5") as hdf:
        hdf_table_list = hdf.keys()
    assert "/trials" in hdf_table_list


def test_tables_in_csv_folder():
    assert "curves" in [file.stem for file in Path("data/csv").iterdir()]
