
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Expense Tracker",
    page_icon="💰",
    layout="wide"
)

st.title("💰 Personal Expense Tracker")
st.write("Upload your CSV or Excel file to analyze your expenses.")

# Upload file
uploaded_file = st.file_uploader(
    "Upload your expense file",
    type=["csv", "xlsx"]
)

# Read uploaded data
if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        # Clean column names
        df.columns = (
            df.columns.astype(str)
            .str.strip()
            .str.lower()
            .str.replace(" ", "_")
        )

        # Required columns
        required_columns = ["date", "category", "amount"]

        missing_columns = [
            col for col in required_columns
            if col not in df.columns
        ]

        if missing_columns:
            st.error(
                "Missing columns: "
                + ", ".join(missing_columns)
                + ". Please check your file format."
            )
            st.info(
                "Required columns: date, category, amount"
            )
            st.stop()

        # Prepare data
        df["date"] = pd.to_datetime(
            df["date"], errors="coerce"
        )
        df["amount"] = pd.to_numeric(
            df["amount"], errors="coerce"
        )
        df["category"] = (
            df["category"].astype("string").str.strip()
        )

        # Remove invalid rows
        df = df.dropna(
            subset=["date", "category", "amount"]
        )
        df = df[df["category"] != ""]

        if df.empty:
            st.warning("No valid expense records found.")
            st.stop()

        # Sidebar filters
        st.sidebar.header("Filter Expenses")

        min_date = df["date"].min().date()
        max_date = df["date"].max().date()

        date_range = st.sidebar.date_input(
            "Select date range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )

        categories = sorted(df["category"].unique())

        selected_categories = st.sidebar.multiselect(
            "Choose categories",
            categories,
            default=categories
        )

        # Apply filters
        filtered_df = df[
            df["category"].isin(selected_categories)
        ].copy()

        if len(date_range) == 2:
            start_date, end_date = date_range

            filtered_df = filtered_df[
                (filtered_df["date"].dt.date >= start_date)
                & (filtered_df["date"].dt.date <= end_date)
            ]

        if filtered_df.empty:
            st.warning("No expenses match your filters.")
            st.stop()

        # Summary metrics
        total_expense = filtered_df["amount"].sum()
        average_expense = filtered_df["amount"].mean()
        highest_expense = filtered_df["amount"].max()
        transaction_count = len(filtered_df)

        st.subheader("Expense Summary")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Total Expenses",
            f"₹{total_expense:,.2f}"
        )
        col2.metric(
            "Average Expense",
            f"₹{average_expense:,.2f}"
        )
        col3.metric(
            "Highest Expense",
            f"₹{highest_expense:,.2f}"
        )
        col4.metric(
            "Transactions",
            transaction_count
        )

        # Category chart
        st.subheader("Expenses by Category")

        category_totals = (
            filtered_df.groupby("category")["amount"]
            .sum()
            .reset_index()
        )

        fig_pie = px.pie(
            category_totals,
            names="category",
            values="amount",
            title="Expense Distribution",
            hole=0.4
        )

        st.plotly_chart(fig_pie, use_container_width=True)

        # Daily expense chart
        st.subheader("Expenses Over Time")

        daily_totals = (
            filtered_df.groupby("date")["amount"]
            .sum()
            .reset_index()
            .sort_values("date")
        )

        fig_line = px.line(
            daily_totals,
            x="date",
            y="amount",
            markers=True,
            title="Daily Spending Trend",
            labels={
                "date": "Date",
                "amount": "Expense (₹)"
            }
        )

        st.plotly_chart(
            fig_line,
            use_container_width=True
        )

        # Transaction table
        st.subheader("Expense Records")
        st.dataframe(
            filtered_df.sort_values(
                "date", ascending=False
            ),
            use_container_width=True,
            hide_index=True
        )

        # Download filtered records
        csv_data = filtered_df.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            label="Download Filtered Expenses",
            data=csv_data,
            file_name="filtered_expenses.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error(f"Could not process the file: {e}")

else:
    st.info(
        "Please upload a CSV or Excel file to get started."
    )

    st.write("Your file must contain these columns:")
    st.code("date, category, amount")

    st.write("Example:")
    example = pd.DataFrame({
        "date": ["2026-10-01", "2026-10-02", "2026-10-03"],
        "category": ["Food", "Travel", "Shopping"],
        "amount": [250, 100, 500],
        "description": [
            "Lunch", "Bus fare", "Clothes"
        ]
    })

    st.dataframe(example, hide_index=True)
