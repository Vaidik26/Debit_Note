# data_verifier.py - Data verification and comparison functions

import pandas as pd


def compare_dataframes(processed_df, expected_df):
    """
    Compare processed DataFrame with expected DataFrame

    Returns:
    - Dictionary with comparison results
    """
    results = {
        "row_comparison": {},
        "column_comparison": {},
        "extra_in_processed": None,
        "missing_in_processed": None,
        "value_mismatches": [],
        "summary": {},
    }

    # Row comparison
    results["row_comparison"] = {
        "processed_rows": len(processed_df),
        "expected_rows": len(expected_df),
        "difference": len(processed_df) - len(expected_df),
    }

    # Column comparison
    processed_cols = set(processed_df.columns)
    expected_cols = set(expected_df.columns)

    results["column_comparison"] = {
        "processed_columns": list(processed_df.columns),
        "expected_columns": list(expected_df.columns),
        "extra_in_processed": list(processed_cols - expected_cols),
        "missing_in_processed": list(expected_cols - processed_cols),
        "columns_match": processed_cols == expected_cols,
    }

    # Find extra/missing customers
    if (
        "Customer Name" in processed_df.columns
        and "Customer Name" in expected_df.columns
    ):
        processed_customers = set(processed_df["Customer Name"].unique())
        expected_customers = set(expected_df["Customer Name"].unique())

        results["extra_in_processed"] = list(processed_customers - expected_customers)
        results["missing_in_processed"] = list(expected_customers - processed_customers)

    # Summary
    results["summary"] = {
        "columns_match": results["column_comparison"]["columns_match"],
        "row_difference": results["row_comparison"]["difference"],
        "extra_customers": len(results["extra_in_processed"])
        if results["extra_in_processed"]
        else 0,
        "missing_customers": len(results["missing_in_processed"])
        if results["missing_in_processed"]
        else 0,
    }

    return results


def get_detailed_mismatches(processed_df, expected_df, key_columns=None):
    """
    Get detailed row-by-row mismatches between two DataFrames

    Parameters:
    - processed_df: Processed DataFrame
    - expected_df: Expected DataFrame
    - key_columns: List of columns to use as keys for matching (default: Customer Name, Transaction#)

    Returns:
    - DataFrame with mismatches
    """
    if key_columns is None:
        key_columns = ["Customer Name", "Transaction#"]

    # Ensure key columns exist in both DataFrames
    for col in key_columns:
        if col not in processed_df.columns or col not in expected_df.columns:
            return pd.DataFrame(
                {"Error": [f"Key column '{col}' not found in one or both DataFrames"]}
            )

    # Create copies to avoid modifying original DataFrames
    proc_df = processed_df.copy()
    exp_df = expected_df.copy()

    # Create composite key
    proc_df["_composite_key"] = proc_df[key_columns].astype(str).agg("||".join, axis=1)
    exp_df["_composite_key"] = exp_df[key_columns].astype(str).agg("||".join, axis=1)

    # Find rows only in processed
    only_in_processed_mask = ~proc_df["_composite_key"].isin(exp_df["_composite_key"])
    only_in_processed = proc_df[only_in_processed_mask].copy()

    # Find rows only in expected
    only_in_expected_mask = ~exp_df["_composite_key"].isin(proc_df["_composite_key"])
    only_in_expected = exp_df[only_in_expected_mask].copy()

    # Build results list
    mismatch_records = []

    # Add extra rows from processed
    for idx, row in only_in_processed.iterrows():
        mismatch_records.append(
            {
                "Mismatch Type": "Extra in Processed",
                "Customer Name": row.get("Customer Name", "N/A"),
                "Transaction#": row.get("Transaction#", "N/A"),
                "Type": row.get("Type", "N/A"),
                "Age": row.get("Age", "N/A"),
                "Balance Due": row.get("Balance Due", "N/A"),
                "Interest Amount": row.get("interest amount", "N/A"),
            }
        )

    # Add missing rows from expected
    for idx, row in only_in_expected.iterrows():
        mismatch_records.append(
            {
                "Mismatch Type": "Missing in Processed",
                "Customer Name": row.get("Customer Name", "N/A"),
                "Transaction#": row.get("Transaction#", "N/A"),
                "Type": row.get("Type", "N/A"),
                "Age": row.get("Age", "N/A"),
                "Balance Due": row.get("Balance Due", "N/A"),
                "Interest Amount": row.get("interest amount", "N/A"),
            }
        )

    if mismatch_records:
        return pd.DataFrame(mismatch_records)

    return pd.DataFrame({"Message": ["No mismatches found! Data matches perfectly."]})


def get_value_comparison(processed_df, expected_df, compare_columns=None):
    """
    Compare values for matching rows

    Parameters:
    - processed_df: Processed DataFrame
    - expected_df: Expected DataFrame
    - compare_columns: Columns to compare (default: interest amount)

    Returns:
    - DataFrame with value comparisons
    """
    if compare_columns is None:
        compare_columns = ["interest amount", "Balance Due", "Age"]

    key_columns = ["Customer Name", "Transaction#"]

    # Create copies to avoid modifying original DataFrames
    proc_df = processed_df.copy()
    exp_df = expected_df.copy()

    # Create composite key
    proc_df["_composite_key"] = proc_df[key_columns].astype(str).agg("||".join, axis=1)
    exp_df["_composite_key"] = exp_df[key_columns].astype(str).agg("||".join, axis=1)

    # Find matching rows
    common_keys = set(proc_df["_composite_key"]) & set(exp_df["_composite_key"])

    if len(common_keys) == 0:
        return pd.DataFrame({"Message": ["No matching rows found for comparison"]})

    comparisons = []
    for key in list(common_keys)[:100]:  # Limit to first 100 for performance
        proc_row = proc_df[proc_df["_composite_key"] == key].iloc[0]
        exp_row = exp_df[exp_df["_composite_key"] == key].iloc[0]

        for col in compare_columns:
            if col in proc_df.columns and col in exp_df.columns:
                proc_val = proc_row[col]
                exp_val = exp_row[col]

                # Check if values are different (with tolerance for floats)
                if pd.notna(proc_val) and pd.notna(exp_val):
                    try:
                        proc_float = float(proc_val)
                        exp_float = float(exp_val)
                        if abs(proc_float - exp_float) > 0.01:  # Tolerance of 0.01
                            comparisons.append(
                                {
                                    "Customer Name": proc_row["Customer Name"],
                                    "Transaction#": proc_row["Transaction#"],
                                    "Column": col,
                                    "Processed Value": proc_val,
                                    "Expected Value": exp_val,
                                    "Difference": round(proc_float - exp_float, 4),
                                }
                            )
                    except (ValueError, TypeError):
                        # Non-numeric comparison
                        if str(proc_val) != str(exp_val):
                            comparisons.append(
                                {
                                    "Customer Name": proc_row["Customer Name"],
                                    "Transaction#": proc_row["Transaction#"],
                                    "Column": col,
                                    "Processed Value": proc_val,
                                    "Expected Value": exp_val,
                                    "Difference": "N/A",
                                }
                            )

    if comparisons:
        return pd.DataFrame(comparisons)

    return pd.DataFrame({"Message": ["All compared values match!"]})


def get_summary_report(processed_df, expected_df):
    """
    Generate a comprehensive summary report

    Returns:
    - Dictionary with summary information
    """
    comparison = compare_dataframes(processed_df, expected_df)

    report = {
        "Total Processed Rows": len(processed_df),
        "Total Expected Rows": len(expected_df),
        "Row Difference": comparison["row_comparison"]["difference"],
        "Columns Match": comparison["column_comparison"]["columns_match"],
        "Extra Customers Count": len(comparison["extra_in_processed"])
        if comparison["extra_in_processed"]
        else 0,
        "Missing Customers Count": len(comparison["missing_in_processed"])
        if comparison["missing_in_processed"]
        else 0,
    }

    # Calculate totals
    if "interest amount" in processed_df.columns:
        report["Processed Total Interest"] = processed_df["interest amount"].sum()
    if "interest amount" in expected_df.columns:
        report["Expected Total Interest"] = expected_df["interest amount"].sum()

    return report
