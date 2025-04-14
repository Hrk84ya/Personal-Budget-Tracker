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
    check_budget_alerts,
    edit_transaction,
    delete_transaction,
    search_transactions,
    get_all_tags
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
            value=datetime.now(),
            key="add_transaction_date"
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
        
        # Add tags input
        tags = st.text_input(
            "Tags (comma-separated)",
            help="Add tags to categorize your transactions (e.g., 'groceries, monthly, essential')"
        )

        if st.button("Add Transaction"):
            if amount > 0 and description:
                st.session_state.transactions = save_transaction(
                    transaction_date,
                    transaction_type,
                    category,
                    amount,
                    description,
                    tags
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

# Transaction Management Section
st.subheader("Transaction Management")

# Search and Filter
col1, col2 = st.columns(2)

with col1:
    search_term = st.text_input("Search transactions", 
                               help="Search in descriptions and tags")
    start_date = st.date_input("Start Date", 
                              value=datetime.now().replace(day=1),
                              key="filter_start_date")
    end_date = st.date_input("End Date", 
                            value=datetime.now(),
                            key="filter_end_date")
    transaction_type_filter = st.selectbox(
        "Transaction Type",
        options=["All", "Expense", "Income"]
    )

with col2:
    category_filter = st.selectbox(
        "Category",
        options=["All"] + categories
    )
    min_amount = st.number_input("Min Amount", min_value=0.0, value=0.0)
    max_amount = st.number_input("Max Amount", min_value=0.0, value=1000000.0)
    tag_filter = st.selectbox(
        "Tag",
        options=["All"] + get_all_tags(st.session_state.transactions)
    )

# Apply filters
filtered_transactions = search_transactions(
    st.session_state.transactions,
    search_term=search_term if search_term else None,
    start_date=start_date,
    end_date=end_date,
    transaction_type=transaction_type_filter if transaction_type_filter != "All" else None,
    category=category_filter if category_filter != "All" else None,
    min_amount=min_amount if min_amount > 0 else None,
    max_amount=max_amount if max_amount < 1000000.0 else None,
    tags=tag_filter if tag_filter != "All" else None
)

# Display filtered transactions with edit/delete options
st.dataframe(
    filtered_transactions.sort_values('date', ascending=False),
    use_container_width=True,
    hide_index=True
)

# Edit Transaction
st.subheader("Edit Transaction")
edit_index = st.number_input("Enter transaction index to edit", 
                            min_value=0, 
                            max_value=len(filtered_transactions)-1 if not filtered_transactions.empty else 0,
                            value=0,
                            key="edit_index")

if not filtered_transactions.empty:
    transaction = filtered_transactions.iloc[edit_index]
    
    col1, col2 = st.columns(2)
    
    with col1:
        edit_date = st.date_input("Date", value=pd.to_datetime(transaction['date']), key="edit_date")
        edit_type = st.selectbox("Type", options=["Expense", "Income"], 
                               index=0 if transaction['type'] == "Expense" else 1,
                               key="edit_type")
        edit_category = st.selectbox("Category", options=categories, 
                                   index=categories.index(transaction['category']),
                                   key="edit_category")
    
    with col2:
        edit_amount = st.number_input("Amount", min_value=0.01, 
                                    value=float(transaction['amount']),
                                    key="edit_amount")
        edit_description = st.text_input("Description", 
                                       value=transaction['description'],
                                       key="edit_description")
        edit_tags = st.text_input("Tags", value=transaction['tags'], key="edit_tags")

    if st.button("Update Transaction"):
        st.session_state.transactions = edit_transaction(
            filtered_transactions.index[edit_index],
            edit_date,
            edit_type,
            edit_category,
            edit_amount,
            edit_description,
            edit_tags
        )
        st.success("Transaction updated successfully!")

# Delete Transaction
st.subheader("Delete Transaction")
delete_index = st.number_input("Enter transaction index to delete", 
                              min_value=0, 
                              max_value=len(filtered_transactions)-1 if not filtered_transactions.empty else 0,
                              value=0,
                              key="delete_index")

if st.button("Delete Transaction"):
    if not filtered_transactions.empty:
        st.session_state.transactions = delete_transaction(filtered_transactions.index[delete_index])
        st.success("Transaction deleted successfully!")
    else:
        st.error("No transactions to delete!")

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center'>
        <p>Made with ❤️ using Streamlit</p>
    </div>
""", unsafe_allow_html=True)