import numpy as np
from pandas.testing import assert_index_equal
import pytest

from src import foos  # noqa

# from src.__main__ import main  # noqa TODO, main test fails


def test_load_files():
    df_1, df_2 = foos.load_files(
        "tests/df_1_file.csv", "tests/df_2_file.csv", None
    )
    assert df_1.shape == (2, 6)
    assert df_2.shape == (2, 6)
    assert list(df_1.columns)[:2] == ["date_1", "int_2"]
    assert list(df_1.iloc[:, -1].values) == ["hello", np.NaN]


def test_load_files_with_valid_index_col():
    df_1, df_2 = foos.load_files(
        "tests/df_1_file.csv", "tests/df_2_file.csv", "str_3"
    )
    assert df_1.shape == (2, 5)
    assert df_2.shape == (2, 5)
    assert list(df_1.columns)[:2] == ["date_1", "int_2"]
    assert list(df_1.index.values) == ["row1", "row2"]


def test_load_files_with_invalid_index_col(capsys):
    with pytest.raises(SystemExit) as exc_info:
        df_1, df_2 = foos.load_files(
            "tests/df_1_file.csv", "tests/df_2_file.csv", "date_1"
        )
        captured = capsys.readouterr()
        assert "Error. Column date_1" in captured.out
        assert exc_info.type is SystemExit


def test_impute_missing_values(df_1_base, df_2_base):
    assert df_1_base.isnull().sum().sum() == 2
    df_1, df_2 = foos.impute_missing_values(df_1_base, df_2_base)
    assert (df_1.values == "MISSING").sum() == 2


def test_check_if_dataframes_are_equal(df_1_base, df_2_base):
    assert foos.check_if_dataframes_are_equal(df_1_base, df_2_base) is False
    assert foos.check_if_dataframes_are_equal(df_1_base, df_1_base)


def test_check_for_same_length(df_1_base, df_2_base, df_1_extended):
    assert foos.check_for_same_length(df_1_base, df_1_extended) is False
    assert foos.check_for_same_length(df_1_base, df_2_base)


def test_check_for_same_width(df_1_base, df_1_extended):
    assert foos.check_for_same_width(df_1_base, df_1_extended)
    df_1_extended = df_1_extended[list(df_1_extended.columns)[1:]]
    assert foos.check_for_same_width(df_1_base, df_1_extended) is False


def test_check_for_identical_column_names(df_1_base, df_1_extended):
    assert foos.check_for_identical_column_names(df_1_base, df_1_extended)
    df_1_extended.columns = ["a", "b", "c", "d", "e", "f"]
    assert (
        foos.check_for_identical_column_names(df_1_base, df_1_extended) is False
    )


def test_check_for_identical_index_values(df_1_base, df_2_base, df_1_extended):
    assert foos.check_for_identical_index_values(df_1_base, df_2_base)
    assert (
        foos.check_for_identical_index_values(df_1_base, df_1_extended) is False
    )


def test_check_for_overlapping_index_values(df_1_base, df_1_extended):
    df_1_extended = foos.check_for_overlapping_index_values(
        df_1_extended, df_1_base
    )
    assert_index_equal(df_1_extended.index, df_1_base.index)

    df_1_base.index = [1, 3]
    with pytest.raises(
        ValueError, match="Cannot compare DFs. Index values do not overlap."
    ) as e:
        foos.check_for_overlapping_index_values(df_1_extended, df_1_base)
        assert e.type is ValueError


def test_check_for_identical_dtypes(df_1_base, df_2_base):
    assert foos.check_for_identical_dtypes(df_1_base, df_1_base)
    assert foos.check_for_identical_dtypes(df_1_base, df_2_base) is False


def test_get_user_input(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "y")
    user_input = foos.get_user_input("dtypes")
    assert user_input == "y"


def test_align_dtypes(df_1_base, df_2_base):
    diff_list, _, _ = foos._align_dtypes(df_1_base, df_2_base)
    assert len(diff_list) == 1
    df_3 = df_1_base.copy()
    df_3["float_4"] = df_3["float_4"].astype(int)
    df_3["date_1"] = df_3["date_1"].astype(object)
    diff_list, _, _ = foos._align_dtypes(df_1_base, df_3)
    assert len(diff_list) == 0


def test_enforce_dtype_identity(df_1_base, df_2_base, capsys):
    df_1, df_2 = foos.enforce_dtype_identity(df_1_base, df_2_base)
    assert list(df_1.dtypes.values) == list(df_2.dtypes.values)
    captured = capsys.readouterr()
    assert captured.out == ""
    df_3 = df_1_base.copy()
    df_3.iloc[0, 3] = "str"
    df_1, df_3 = foos.enforce_dtype_identity(df_1_base, df_3)
    assert list(df_1.dtypes.values) != list(df_3.dtypes.values)
    captured = capsys.readouterr()
    assert "float_4" in captured.out


def test_get_subsets(df_1_base, df_1_extended):
    common, only_1, only_2 = foos._get_subsets(
        "index", df_1_base, df_1_extended
    )
    assert (only_1 == set()) and (only_2 == set([2]))
    df_3 = df_1_extended.copy()
    colnames = list(df_3.columns)
    colnames[0] = "xxx"
    df_3.columns = colnames
    common, only_1, only_2 = foos._get_subsets("columns", df_1_base, df_3)
    assert (only_1 == set(["date_1"])) and (only_2 == set(["xxx"]))


def test_handle_different_values(df_1_base, df_1_extended):
    pass  # TODO


def test_handle_different_length(df_1_base, df_2_base, df_1_extended):
    df_1, df_2 = foos.handle_different_length(df_1_extended, df_1_base)
    assert len(df_1) == len(df_2)

    df_1, df_2 = foos.handle_different_length(df_1_base, df_1_extended)
    assert len(df_1) == len(df_2)

    with pytest.raises(
        AssertionError, match="Something strange happened ..."
    ) as e:
        foos.handle_different_length(df_1_base, df_2_base)
        assert e.type is AssertionError

    df_2_base.index = [0, 2]
    with pytest.raises(
        ValueError, match="Cannot compare DFs. Index values are not identical."
    ) as e:
        foos.handle_different_length(df_1_base, df_2_base)
        assert e.type is ValueError


def test_check_for_overlapping_column_names(df_1_base, df_1_extended):
    df_1_base = df_1_base[list(df_1_base.columns)[1:]]
    df_1_extended = foos.check_for_overlapping_column_names(
        df_1_extended, df_1_base
    )
    assert df_1_extended.shape[1] == df_1_base.shape[1]

    df_1_base.columns = ["a", "b", "c", "d", "e"]
    with pytest.raises(
        ValueError, match="Cannot compare DFs. Column names do not overlap."
    ) as e:
        foos.check_for_overlapping_column_names(df_1_extended, df_1_base)
        assert e.type is ValueError


def test_handle_different_width(df_1_base, df_2_base, df_1_extended):
    df_1_extended = df_1_extended[list(df_1_extended.columns)[1:]]
    df_1, df_2 = foos.handle_different_width(df_1_extended, df_1_base)
    assert df_1.shape[1] == df_2.shape[1]

    df_1, df_2 = foos.handle_different_width(df_1_base, df_1_extended)
    assert df_1.shape[1] == df_2.shape[1]

    with pytest.raises(
        AssertionError, match="Something strange happened ..."
    ) as e:
        foos.handle_different_width(df_1_base, df_2_base)
        assert e.type is AssertionError

    df_2_base.columns = ["a", "b", "c", "d", "e", "f"]
    with pytest.raises(
        ValueError, match="Cannot compare DFs. Column names are not identical."
    ) as e:
        foos.handle_different_width(df_1_base, df_2_base)
        assert e.type is ValueError


def test_compare(df_1_base, df_2_base, capsys):
    # NaN values have to be eliminated for this test
    df_1, df_2 = foos.impute_missing_values(df_1_base, df_2_base)

    foos.compare(df_1, df_1)
    captured = capsys.readouterr()  # Capture output
    assert "Matching subsets of DFs are identical" in captured.out

    foos.compare(df_1, df_2)
    captured = capsys.readouterr()  # Capture output
    assert "Successfully compared. DFs are NOT indentical." in captured.out


# def test_main(capsys):
#     main("tests/df_1_file.csv", "tests/df_1_file.csv", None)
#     captured = capsys.readouterr()  # Capture output
#     assert "Successfully compared, DFs are identical" in captured.out

#     main("tests/df_1_file.csv", "tests/df_2_file.csv", None)
#     captured = capsys.readouterr()  # Capture output
#     assert "Successfully compared. DFs are NOT indentical." in captured.out

#     main("tests/df_1_file.csv", "tests/df_1_ex_file.csv", None)
#     captured = capsys.readouterr()  # Capture output
#     assert (
#         "Successfully compared. Matching subsets of DFs are identical."
#         in captured.out
#     )

#     main("tests/df_1_file.csv", "tests/df_1_empty_row_file.csv", None)
#     captured = capsys.readouterr()  # Capture output
#     assert "Successfully compared. DFs are NOT indentical." in captured.out

#     with pytest.raises(
#         ValueError, match="Cannot compare DFs. Column names are not identical."
#     ) as e:
#         main("tests/df_1_file.csv", "tests/df_1_alt_col_file.csv", None)
#         assert e.type is ValueError
