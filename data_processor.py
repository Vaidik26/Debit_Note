# data_processor.py - Data processing functions

import pandas as pd
from config import COLUMNS_TO_DROP, FINAL_COLUMNS


def clean_currency_column(series):
    """
    Clean currency column by removing rupee symbol and commas
    Returns numeric series
    """
    cleaned = (
        series.astype(str)
        .str.replace("₹", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.strip()
    )
    return pd.to_numeric(cleaned, errors="coerce")


def clean_age_column(series):
    """
    Clean Age column by removing ' Days' text
    Returns numeric series
    """
    cleaned = series.astype(str).str.replace(" Days", "", regex=False).str.strip()
    return pd.to_numeric(cleaned, errors="coerce")


def process_excel(df, due_days, daily_rate, working_days, ob_age):
    """
    Process raw Excel data and calculate interest

    Parameters:
    - df: Raw DataFrame
    - due_days: Due days threshold for filtering
    - daily_rate: Per day interest rate percentage
    - working_days: Number of working days for interest calculation (used as cap)
    - ob_age: Age value for Customer Opening Balance entries

    Returns:
    - Processed DataFrame with interest calculations
    """
    # Filter only Overdue status rows
    df_filtered = df[df["Status"] == "Overdue"].copy()

    # Remove unnecessary columns if they exist
    df_filtered = df_filtered.drop(
        columns=[col for col in COLUMNS_TO_DROP if col in df_filtered.columns]
    )

    # Clean Balance Due column
    df_filtered["Balance Due"] = clean_currency_column(
        df_filtered["Balance Due"]
    ).fillna(0)

    # Clean Amount column
    df_filtered["Amount"] = clean_currency_column(df_filtered["Amount"])

    # Clean Age column
    df_filtered["Age"] = clean_age_column(df_filtered["Age"])

    # For Customer Opening Balance rows, set Age to specified value
    df_filtered.loc[df_filtered["Type"] == "Customer Opening Balance", "Age"] = ob_age

    # Filter only rows where Age is greater than Due days threshold
    df_filtered = df_filtered[df_filtered["Age"] > due_days].copy()

    # Sort by Customer Name alphabetically
    df_filtered = df_filtered.sort_values("Customer Name").reset_index(drop=True)

    # Add Due days column
    df_filtered["Due days"] = due_days

    # Calculate interest working days dynamically based on Age
    # Formula: interst working = Age - Due days (capped at working_days if needed)
    df_filtered["interst working"] = df_filtered["Age"] - due_days

    # Calculate Previous interest days (days before current working period)
    # Formula: Previous interst = Age - Due days - interst working = 0 for first period
    # But for periods beyond the first, it's cumulative previous days
    df_filtered["Previous interst"] = (
        df_filtered["Age"] - due_days - df_filtered["interst working"]
    ).clip(lower=0)

    # Add per day interest rate column
    df_filtered["per day interst%"] = daily_rate

    # Calculate working interest percentage based on actual working days
    # Formula: working interst in % = interst working * per day interst%
    df_filtered["working interst in %"] = df_filtered["interst working"] * daily_rate

    # Calculate interest amount based on balance due
    # Formula: interest amount = Balance Due * (working interst in % / 100)
    df_filtered["interest amount"] = df_filtered["Balance Due"] * (
        df_filtered["working interst in %"] / 100
    )

    # Round interest amount to 4 decimal places
    df_filtered["interest amount"] = df_filtered["interest amount"].round(4)

    # Return dataframe with reordered columns
    return df_filtered[FINAL_COLUMNS]
