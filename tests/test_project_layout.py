import os
from pathlib import Path
import pandas as pd
from hypothesis import given
from hypothesis.strategies import lists, text


def test_data_exists():
    assert os.path.isfile("data/data.h5")


@given(lists(text()))
def test_create_hd5_from_csvs(csv_file_list):
    csv_name_list = [file.stem for file in Path("data/csv").iterdir()]
    with pd.HDFStore("data/data.h5") as hdf:
        hdf_table_list = hdf.keys()
    assert hdf_table_list == csv_name_list
