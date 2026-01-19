# utils.py - Utility functions

import pandas as pd
from io import BytesIO


def to_excel_bytes(df, sheet_name="Sheet1"):
    """
    Convert DataFrame to Excel bytes for download

    Parameters:
    - df: DataFrame to convert
    - sheet_name: Name of the Excel sheet

    Returns:
    - Bytes object containing Excel file
    """
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    return output.getvalue()


def validate_input_columns(df, required_columns):
    """
    Validate that DataFrame has required columns

    Parameters:
    - df: DataFrame to validate
    - required_columns: List of required column names

    Returns:
    - Tuple of (is_valid, missing_columns)
    """
    df_columns = set(df.columns)
    required = set(required_columns)
    missing = required - df_columns

    return len(missing) == 0, list(missing)


def get_summary_stats(df, column_name):
    """
    Get summary statistics for a numeric column

    Parameters:
    - df: DataFrame
    - column_name: Name of the column

    Returns:
    - Dictionary with sum, mean, max, min
    """
    if column_name not in df.columns:
        return None

    return {
        "sum": df[column_name].sum(),
        "mean": df[column_name].mean(),
        "max": df[column_name].max(),
        "min": df[column_name].min(),
    }
