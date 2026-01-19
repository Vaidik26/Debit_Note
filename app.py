# app.py - Main Streamlit application with modular structure

import streamlit as st
import pandas as pd

# Import modules
from config import (
    DEFAULT_DUE_DAYS_THRESHOLD,
    DEFAULT_PER_DAY_INTEREST_RATE,
    DEFAULT_INTEREST_WORKING_DAYS,
    DEFAULT_OPENING_BALANCE_AGE,
    REQUIRED_INPUT_COLUMNS,
)
from data_processor import process_excel
from data_verifier import (
    compare_dataframes,
    get_detailed_mismatches,
    get_value_comparison,
)
from utils import to_excel_bytes, validate_input_columns, get_summary_stats


# Page configuration
st.set_page_config(
    page_title="Invoice To Debit Note Converter", page_icon="📊", layout="wide"
)


def render_sidebar():
    """Render sidebar with configuration options"""
    st.sidebar.header("⚙️ Configuration")

    # Due days threshold
    due_days = st.sidebar.number_input(
        "Due Days Threshold",
        min_value=1,
        max_value=365,
        value=DEFAULT_DUE_DAYS_THRESHOLD,
        help="Number of days after which interest is calculated",
    )

    # Per day interest rate
    daily_rate = st.sidebar.number_input(
        "Per Day Interest Rate (%)",
        min_value=0.01,
        max_value=1.0,
        value=DEFAULT_PER_DAY_INTEREST_RATE,
        format="%.2f",
        help="Daily interest rate percentage",
    )

    # Interest working days
    working_days = st.sidebar.number_input(
        "Interest Working Days",
        min_value=1,
        max_value=31,
        value=DEFAULT_INTEREST_WORKING_DAYS,
        help="Number of days for current interest calculation period",
    )

    # Opening balance age
    ob_age = st.sidebar.number_input(
        "Opening Balance Age",
        min_value=150,
        max_value=500,
        value=DEFAULT_OPENING_BALANCE_AGE,
        help="Age value to assign to Customer Opening Balance entries",
    )

    return due_days, daily_rate, working_days, ob_age


def render_data_processing_tab(config):
    """Render the data processing tab"""
    due_days, daily_rate, working_days, ob_age = config

    st.header("📁 Data Processing")
    st.markdown("Upload your raw Excel file to process and calculate interest")

    # File uploader
    uploaded_file = st.file_uploader(
        "Upload your raw Excel file", type=["xlsx", "xls"], key="process_uploader"
    )

    if uploaded_file is not None:
        # Read the uploaded file
        df_raw = pd.read_excel(uploaded_file)

        # Validate input columns
        is_valid, missing = validate_input_columns(df_raw, REQUIRED_INPUT_COLUMNS)

        if not is_valid:
            st.error(f"Missing required columns: {', '.join(missing)}")
            return None

        # Display original data info
        st.subheader("📋 Original Data")
        col1, col2 = st.columns(2)
        col1.metric("Total Rows", df_raw.shape[0])
        col2.metric("Total Columns", df_raw.shape[1])

        # Show preview
        with st.expander("View Original Data Preview"):
            st.dataframe(df_raw.head(10), use_container_width=True)

        st.divider()

        # Process the data
        try:
            df_processed = process_excel(
                df_raw, due_days, daily_rate, working_days, ob_age
            )

            # Store in session state for verification tab
            st.session_state["processed_data"] = df_processed

            # Display processed data info
            st.subheader("✅ Processed Data")
            col1, col2, col3 = st.columns(3)
            col1.metric("Filtered Rows", df_processed.shape[0])
            col2.metric("Output Columns", df_processed.shape[1])

            # Get summary stats
            stats = get_summary_stats(df_processed, "interest amount")
            if stats:
                col3.metric("Total Interest", f"₹{stats['sum']:,.2f}")

            # Show processed data
            st.dataframe(df_processed, use_container_width=True)

            st.divider()

            # Summary statistics
            st.subheader("📈 Summary Statistics")
            if stats:
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Total Interest", f"₹{stats['sum']:,.2f}")
                col2.metric("Average Interest", f"₹{stats['mean']:,.2f}")
                col3.metric("Max Interest", f"₹{stats['max']:,.2f}")
                col4.metric("Min Interest", f"₹{stats['min']:,.2f}")

            # Download button
            excel_data = to_excel_bytes(df_processed, "Interest Calculation")
            st.download_button(
                label="📥 Download Processed Excel",
                data=excel_data,
                file_name="interest_calculated_output.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

            return df_processed

        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
            return None

    else:
        st.info("👆 Please upload an Excel file to get started")

        # Show expected columns
        with st.expander("📋 Expected Input Columns"):
            st.markdown("""
            Your Excel file should contain these columns:
            - **Region**: Geographic region
            - **Area Name**: Area within region
            - **Market**: Market name
            - **Customer Name**: Customer's full name
            - **Customer Number**: Unique customer ID
            - **DATE**: Transaction date
            - **Transaction#**: Transaction reference number
            - **Type**: Transaction type
            - **Status**: Payment status (must include "Overdue" values)
            - **Due Date**: Payment due date
            - **Amount**: Original transaction amount (can have ₹ symbol)
            - **Balance Due**: Remaining balance (can have ₹ symbol)
            - **Age**: Days since transaction (can be in format "260 Days")
            """)

        return None


def render_data_verification_tab():
    """Render the data verification tab"""
    st.header("🔍 Data Verification")
    st.markdown("Upload expected output file to compare with processed data")

    # Check if processed data exists
    if (
        "processed_data" not in st.session_state
        or st.session_state["processed_data"] is None
    ):
        st.warning(
            "⚠️ No processed data available. Please process a file in the 'Data Processing' tab first."
        )
        return

    processed_df = st.session_state["processed_data"]

    # Show processed data summary
    st.subheader("📊 Processed Data Summary")
    col1, col2 = st.columns(2)
    col1.metric("Processed Rows", len(processed_df))
    col2.metric("Processed Columns", len(processed_df.columns))

    st.divider()

    # File uploader for expected data
    expected_file = st.file_uploader(
        "Upload expected output Excel file for comparison",
        type=["xlsx", "xls"],
        key="verify_uploader",
    )

    if expected_file is not None:
        # Read expected file
        expected_df = pd.read_excel(expected_file)

        st.subheader("📋 Expected Data Summary")
        col1, col2 = st.columns(2)
        col1.metric("Expected Rows", len(expected_df))
        col2.metric("Expected Columns", len(expected_df.columns))

        st.divider()

        # Compare dataframes
        results = compare_dataframes(processed_df, expected_df)

        # Display comparison results
        st.subheader("📊 Comparison Results")

        # Row comparison
        col1, col2, col3 = st.columns(3)
        col1.metric("Processed Rows", results["row_comparison"]["processed_rows"])
        col2.metric("Expected Rows", results["row_comparison"]["expected_rows"])

        row_diff = results["row_comparison"]["difference"]
        if row_diff > 0:
            col3.metric(
                "Row Difference", f"+{row_diff}", delta=row_diff, delta_color="inverse"
            )
        elif row_diff < 0:
            col3.metric(
                "Row Difference", str(row_diff), delta=row_diff, delta_color="inverse"
            )
        else:
            col3.metric("Row Difference", "0 ✅", delta=0, delta_color="off")

        st.divider()

        # Column comparison
        st.subheader("📋 Column Comparison")

        if results["column_comparison"]["columns_match"]:
            st.success("✅ All columns match!")
        else:
            if results["column_comparison"]["extra_in_processed"]:
                st.warning(
                    f"⚠️ Extra columns in processed: {', '.join(results['column_comparison']['extra_in_processed'])}"
                )
            if results["column_comparison"]["missing_in_processed"]:
                st.error(
                    f"❌ Missing columns in processed: {', '.join(results['column_comparison']['missing_in_processed'])}"
                )

        st.divider()

        # Customer comparison
        st.subheader("👥 Customer Comparison")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Extra Customers in Processed:**")
            if results["extra_in_processed"]:
                for customer in results["extra_in_processed"]:
                    st.write(f"➕ {customer}")
            else:
                st.success("No extra customers")

        with col2:
            st.markdown("**Missing Customers in Processed:**")
            if results["missing_in_processed"]:
                for customer in results["missing_in_processed"]:
                    st.write(f"➖ {customer}")
            else:
                st.success("No missing customers")

        st.divider()

        # Detailed mismatches
        st.subheader("🔍 Detailed Row Mismatches")

        mismatches = get_detailed_mismatches(processed_df, expected_df)

        if "Message" in mismatches.columns:
            st.success(mismatches["Message"].iloc[0])
        else:
            st.dataframe(mismatches, use_container_width=True)

            # Download mismatches
            if len(mismatches) > 0:
                mismatch_excel = to_excel_bytes(mismatches, "Mismatches")
                st.download_button(
                    label="📥 Download Mismatches Report",
                    data=mismatch_excel,
                    file_name="data_mismatches.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )

        st.divider()

        # Value comparison for matching rows
        st.subheader("🔢 Value Comparison (Matching Rows)")

        value_comp = get_value_comparison(processed_df, expected_df)

        if "Message" in value_comp.columns:
            st.success(value_comp["Message"].iloc[0])
        else:
            st.warning(f"Found {len(value_comp)} value differences")
            st.dataframe(value_comp, use_container_width=True)

    else:
        st.info("👆 Upload an expected output file to compare with processed data")


def render_help_tab():
    """Render the help/documentation tab"""
    st.header("📚 Help & Documentation")

    st.markdown("""
    ## How to Use This Application
    
    ### 1. Data Processing Tab
    - Upload your raw Excel file containing invoice data
    - Configure the calculation parameters in the sidebar
    - View and download the processed output with interest calculations
    
    ### 2. Data Verification Tab
    - First, process a file in the Data Processing tab
    - Then upload an expected output file to compare
    - View detailed comparison results including:
      - Row count differences
      - Column differences
      - Extra/missing customers
      - Value mismatches
    
    ### Configuration Options
    
    | Option | Description | Default |
    |--------|-------------|---------|
    | Due Days Threshold | Days after which interest is calculated | 150 |
    | Per Day Interest Rate | Daily interest rate (%) | 0.06 |
    | Interest Working Days | Working days for calculation | 31 |
    | Opening Balance Age | Age for Customer Opening Balance | 300 |
    
    ### Interest Calculation Formula
    
    ```
    Working Interest % = Interest Working Days × Per Day Interest Rate
    Interest Amount = Balance Due × (Working Interest % / 100)
    Previous Interest = Age - Due Days Threshold - Interest Working Days
    ```
    
    ### Required Input Columns
    
    Your raw Excel file must contain these columns:
    - Region, Area Name, Market
    - Customer Name, Customer Number
    - DATE, Transaction#, Type, Status
    - Due Date, Amount, Balance Due, Age
    
    ### Output Columns
    
    The processed output will contain all input columns plus:
    - Due days, Previous interst, interst working
    - per day interst%, working interst in %, interest amount
    """)


def main():
    """Main application function"""
    # Title
    st.title("📊 Invoice To Debit Note Converter")
    st.markdown(
        "Convert raw Invoice data to Debit Note format with interest calculations"
    )

    # Render sidebar and get configuration
    config = render_sidebar()

    st.divider()

    # Create tabs
    tab1, tab2, tab3 = st.tabs(
        ["📁 Data Processing", "🔍 Data Verification", "📚 Help"]
    )

    with tab1:
        render_data_processing_tab(config)

    with tab2:
        render_data_verification_tab()

    with tab3:
        render_help_tab()

    # Footer
    st.divider()
    st.markdown("<center>Made with ❤️ using Streamlit</center>", unsafe_allow_html=True)


# Run the app
if __name__ == "__main__":
    main()
