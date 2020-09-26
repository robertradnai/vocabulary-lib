import os
import shutil

TEST_DICT_PATH = "testdata_temp/testdict.xlsx"
TEST_DICT_PARQUET_PATH = "testdata_temp/testdict.parquet"
TEST_DICT_OUT_PATH = "testdata_temp/testdict_out.xlsx"


def reset_test_env():
    # Delete and re-create test data folder so that the app can't accidentally
    #  overwrite the original test data.
    test_data = 'testdata'
    temp_folder = 'testdata_temp'
    if os.path.exists(temp_folder):
        shutil.rmtree(temp_folder)
    shutil.copytree(test_data, temp_folder)
