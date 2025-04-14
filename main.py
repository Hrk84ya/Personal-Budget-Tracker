import streamlit as st
import pandas as pd
from datetime import datetime
from utils import (
    load_transactions,
    save_transaction,
    get_category_distribution,
    get_monthly_trends,
    get_monthly_summary,
    export_to_excel,
    export_to_csv,
    load_budgets,
    save_budget,
    get_budget_status,
    get_budget_vs_actual_chart,
    check_budget_alerts
)

# Page configuration
st.set_page_config(
    page_title="Personal Budget Tracker",
    page_icon="💰",
    layout="wide"
)

# Initialize session state
if 'transactions' not in st.session_state:
    st.session_state.transactions = load_transactions()
if 'budgets' not in st.session_state:
    st.session_state.budgets = load_budgets()

# Title and description
st.title("💰 Personal Budget Tracker")
st.markdown("""
    Keep track of your expenses and income with this simple budget tracker.
    Add transactions, view spending patterns, and monitor your financial health.
""")

# Sidebar for adding transactions and managing budgets
with st.sidebar:
    tab1, tab2 = st.tabs(["Add Transaction", "Manage Budgets"])
    
    with tab1:
        st.header("Add New Transaction")

        transaction_date = st.date_input(
            "Date",
            value=datetime.now()
        )

        transaction_type = st.selectbox(
            "Transaction Type",
            options=["Expense", "Income"]
        )

        categories = [
            "Food & Dining",
            "Transportation",
            "Housing",
            "Utilities",
            "Entertainment",
            "Shopping",
            "Healthcare",
            "Education",
            "Salary",
            "Investment",
            "Other"
        ]

        category = st.selectbox("Category", options=categories)

        amount = st.number_input(
            "Amount",
            min_value=0.01,
            format="%f"
        )

        description = st.text_input("Description")

        if st.button("Add Transaction"):
            if amount > 0 and description:
                st.session_state.transactions = save_transaction(
                    transaction_date,
                    transaction_type,
                    category,
                    amount,
                    description
                )
                st.success("Transaction added successfully!")
            else:
                st.error("Please fill in all fields correctly.")

    with tab2:
        st.header("Set Budget Limits")
        for category in categories:
            current_limit = st.session_state.budgets[
                st.session_state.budgets['category'] == category
            ]['monthly_limit'].iloc[0]
            
            new_limit = st.number_input(
                f"Monthly Budget for {category}",
                min_value=0.0,
                value=float(current_limit),
                format="%f"
            )
            
            if new_limit != current_limit:
                st.session_state.budgets = save_budget(category, new_limit)
                st.success(f"Budget updated for {category}!")

# Main content area
col1, col2, col3 = st.columns(3)

# Monthly summary
income, expenses, balance = get_monthly_summary(st.session_state.transactions)

with col1:
    st.metric("Monthly Income", f"₹{income:,.2f}", delta=None)

with col2:
    st.metric("Monthly Expenses", f"₹{expenses:,.2f}", delta=None)

with col3:
    st.metric("Monthly Balance", f"₹{balance:,.2f}", 
              delta=balance, delta_color="normal")

# Budget Alerts
st.subheader("Budget Alerts")
alerts = check_budget_alerts(st.session_state.transactions, st.session_state.budgets)
if alerts:
    for alert in alerts:
        st.warning(alert)
else:
    st.success("No budget alerts at this time!")

# Budget vs Actual Comparison
st.subheader("Budget Analysis")
st.plotly_chart(
    get_budget_vs_actual_chart(st.session_state.transactions, st.session_state.budgets),
    use_container_width=True
)

# Budget Status Table
st.subheader("Budget Status")
budget_status = get_budget_status(st.session_state.transactions, st.session_state.budgets)
st.dataframe(
    budget_status[['category', 'monthly_limit', 'amount', 'percentage', 'status']].rename(
        columns={
            'monthly_limit': 'Budget Limit',
            'amount': 'Actual Spending',
            'percentage': 'Percentage Used',
            'status': 'Status'
        }
    ),
    use_container_width=True,
    hide_index=True
)

# Export section
st.subheader("Export Data")
col1, col2 = st.columns(2)

with col1:
    if st.download_button(
        label="Download as Excel",
        data=export_to_excel(st.session_state.transactions),
        file_name="budget_tracker.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    ):
        st.success("Excel file downloaded successfully!")

with col2:
    if st.download_button(
        label="Download as CSV",
        data=export_to_csv(st.session_state.transactions),
        file_name="budget_tracker.csv",
        mime="text/csv"
    ):
        st.success("CSV file downloaded successfully!")

# Visualizations
st.subheader("Spending Analysis")
col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(
        get_category_distribution(st.session_state.transactions),
        use_container_width=True
    )

with col2:
    st.plotly_chart(
        get_monthly_trends(st.session_state.transactions),
        use_container_width=True
    )

# Transaction History
st.subheader("Transaction History")
st.dataframe(
    st.session_state.transactions.sort_values('date', ascending=False),
    use_container_width=True,
    hide_index=True
)

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center'>
        <p>Made with ❤️ using Streamlit</p>
    </div>
""", unsafe_allow_html=True)