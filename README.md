# 📊 Invoice To Debit Note Converter

A Streamlit web application that converts raw invoice data to debit note format with interest calculations.

## Features

- **Data Processing**: Upload raw Excel files and process them with configurable interest calculations
- **Data Verification**: Compare processed output with expected output to identify mismatches
- **Configurable Parameters**: Adjust due days threshold, interest rate, working days, and more
- **Export to Excel**: Download processed data as Excel files

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Vaidik26/Debit_Note.git
cd Debit_Note
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run app.py
```

## Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| Due Days Threshold | Days after which interest is calculated | 150 |
| Per Day Interest Rate | Daily interest rate (%) | 0.06 |
| Interest Working Days | Working days for calculation | 31 |
| Opening Balance Age | Age for Customer Opening Balance | 300 |

## Interest Calculation Formula

```
Working Interest % = Interest Working Days × Per Day Interest Rate
Interest Amount = Balance Due × (Working Interest % / 100)
Previous Interest = Age - Due Days Threshold - Interest Working Days
```

## Required Input Columns

Your raw Excel file must contain these columns:
- Region, Area Name, Market
- Customer Name, Customer Number
- DATE, Transaction#, Type, Status
- Due Date, Amount, Balance Due, Age

## Project Structure

```
├── app.py              # Main Streamlit application
├── config.py           # Configuration constants
├── data_processor.py   # Data processing functions
├── data_verifier.py    # Data verification functions
├── utils.py            # Utility functions
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

## License

MIT License

## Author

Vaidik
