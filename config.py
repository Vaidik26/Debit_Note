# config.py - Configuration constants and default values

# Default configuration values
DEFAULT_DUE_DAYS_THRESHOLD = 150
DEFAULT_PER_DAY_INTEREST_RATE = 0.06
DEFAULT_INTEREST_WORKING_DAYS = 31
DEFAULT_OPENING_BALANCE_AGE = 300

# Columns to drop from raw data
COLUMNS_TO_DROP = ["Sales person", "Sale Person"]

# Final output column order
FINAL_COLUMNS = [
    "Region",
    "Area Name",
    "Market",
    "Customer Name",
    "Customer Number",
    "DATE",
    "Transaction#",
    "Type",
    "Status",
    "Due Date",
    "Amount",
    "Balance Due",
    "Age",
    "Due days",
    "Previous interst",
    "interst working",
    "per day interst%",
    "working interst in %",
    "interest amount",
]

# Required input columns for validation
REQUIRED_INPUT_COLUMNS = [
    "Region",
    "Area Name",
    "Market",
    "Customer Name",
    "Customer Number",
    "DATE",
    "Transaction#",
    "Type",
    "Status",
    "Due Date",
    "Amount",
    "Balance Due",
    "Age",
]
