# Check the expected file interst working values
import pandas as pd

expected_df = pd.read_excel("expected_output.xlsx")

print("Unique interst working values:")
print(expected_df["interst working"].unique())

print("\nValue counts:")
print(expected_df["interst working"].value_counts())

# Check if interst working ever equals Age - Due days
expected_df["calculated_working"] = expected_df["Age"] - expected_df["Due days"]
expected_df["match"] = (
    expected_df["interst working"] == expected_df["calculated_working"]
)

print("\nDoes interst working match (Age - Due days)?")
print(expected_df["match"].value_counts())

# Show some examples where it matches
matches = expected_df[expected_df["match"] == True]
print(f"\nMatching rows: {len(matches)}")
if len(matches) > 0:
    print(
        matches[
            [
                "Customer Name",
                "Age",
                "Due days",
                "interst working",
                "calculated_working",
            ]
        ].head()
    )

# Show some examples where it doesn't match
non_matches = expected_df[expected_df["match"] == False]
print(f"\nNon-matching rows: {len(non_matches)}")
if len(non_matches) > 0:
    print(
        non_matches[
            [
                "Customer Name",
                "Age",
                "Due days",
                "interst working",
                "calculated_working",
            ]
        ].head()
    )
