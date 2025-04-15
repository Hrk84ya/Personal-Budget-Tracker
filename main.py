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
    get_all_tags,
    load_goals,
    save_goal,
    update_goal,
    delete_goal,
    get_goal_progress_chart,
    get_milestone_chart,
    load_portfolio,
    save_investment,
    update_investment,
    delete_investment,
    get_portfolio_summary,
    get_portfolio_distribution
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
if 'goals' not in st.session_state:
    st.session_state.goals = load_goals()
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = load_portfolio()

# Title and description
st.title("💰 Personal Budget Tracker")
st.markdown("""
    Keep track of your expenses and income with this simple budget tracker.
    Add transactions, view spending patterns, and monitor your financial health.
""")

# Sidebar for adding transactions and managing budgets
with st.sidebar:
    tab1, tab2, tab3, tab4 = st.tabs(["Add Transaction", "Manage Budgets", "Financial Goals", "Investment Portfolio"])
    
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

    with tab3:
        st.header("Financial Goals")
        
        # Add new goal
        st.subheader("Add New Goal")
        goal_type = st.selectbox(
            "Goal Type",
            options=["Savings", "Investment"],
            key="new_goal_type"
        )
        goal_name = st.text_input("Goal Name", key="new_goal_name")
        target_amount = st.number_input(
            "Target Amount",
            min_value=0.01,
            value=1000.0,
            key="new_goal_target"
        )
        current_amount = st.number_input(
            "Current Amount",
            min_value=0.0,
            value=0.0,
            key="new_goal_current"
        )
        deadline = st.date_input(
            "Deadline",
            value=datetime.now().replace(year=datetime.now().year + 1),
            key="new_goal_deadline"
        )
        status = st.selectbox(
            "Status",
            options=["In Progress", "Completed", "On Hold"],
            key="new_goal_status"
        )
        milestones = st.text_input(
            "Milestones (comma-separated)",
            help="Add milestone amounts (e.g., '1000,2000,3000')",
            key="new_goal_milestones"
        )
        
        if st.button("Add Goal"):
            if goal_name and target_amount > 0:
                st.session_state.goals = save_goal(
                    goal_type,
                    goal_name,
                    target_amount,
                    current_amount,
                    deadline,
                    status,
                    milestones
                )
                st.success("Goal added successfully!")
            else:
                st.error("Please fill in all required fields correctly.")
                
    with tab4:
        st.header("Investment Portfolio")
        
        # Add new investment
        st.subheader("Add New Investment")
        investment_type = st.selectbox(
            "Investment Type",
            options=["Stocks", "Bonds", "Mutual Funds", "Crypto", "Other"],
            key="new_investment_type"
        )
        investment_name = st.text_input("Investment Name", key="new_investment_name")
        amount = st.number_input(
            "Amount Invested",
            min_value=0.01,
            value=1000.0,
            key="new_investment_amount"
        )
        purchase_date = st.date_input(
            "Purchase Date",
            value=datetime.now(),
            key="new_investment_date"
        )
        current_value = st.number_input(
            "Current Value",
            min_value=0.0,
            value=1000.0,
            key="new_investment_value"
        )
        
        if st.button("Add Investment"):
            if investment_name and amount > 0:
                st.session_state.portfolio = save_investment(
                    investment_type,
                    investment_name,
                    amount,
                    purchase_date,
                    current_value
                )
                st.success("Investment added successfully!")
            else:
                st.error("Please fill in all required fields correctly.")

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

# Financial Goals Section
st.header("Financial Goals")

# Goal Progress
st.subheader("Goal Progress")
st.plotly_chart(
    get_goal_progress_chart(st.session_state.goals),
    use_container_width=True
)

# Goals Table
st.subheader("Your Goals")
if not st.session_state.goals.empty:
    st.dataframe(
        st.session_state.goals,
        use_container_width=True,
        hide_index=True
    )
    
    # Edit Goal
    st.subheader("Edit Goal")
    edit_goal_index = st.number_input(
        "Enter goal index to edit", 
        min_value=0, 
        max_value=len(st.session_state.goals)-1,
        value=0,
        key="edit_goal_index"
    )
    
    goal = st.session_state.goals.iloc[edit_goal_index]
    
    col1, col2 = st.columns(2)
    
    with col1:
        edit_goal_type = st.selectbox(
            "Goal Type",
            options=["Savings", "Investment"],
            index=0 if goal['goal_type'] == "Savings" else 1,
            key="edit_goal_type"
        )
        edit_goal_name = st.text_input(
            "Goal Name", 
            value=goal['name'],
            key="edit_goal_name"
        )
        edit_target_amount = st.number_input(
            "Target Amount",
            min_value=0.01,
            value=float(goal['target_amount']),
            key="edit_goal_target"
        )
        edit_current_amount = st.number_input(
            "Current Amount",
            min_value=0.0,
            value=float(goal['current_amount']),
            key="edit_goal_current"
        )
    
    with col2:
        edit_deadline = st.date_input(
            "Deadline",
            value=pd.to_datetime(goal['deadline']),
            key="edit_goal_deadline"
        )
        edit_status = st.selectbox(
            "Status",
            options=["In Progress", "Completed", "On Hold"],
            index=["In Progress", "Completed", "On Hold"].index(goal['status']),
            key="edit_goal_status"
        )
        edit_milestones = st.text_input(
            "Milestones (comma-separated)",
            value=goal['milestones'],
            key="edit_goal_milestones"
        )
    
    if st.button("Update Goal"):
        st.session_state.goals = update_goal(
            edit_goal_index,
            edit_goal_type,
            edit_goal_name,
            edit_target_amount,
            edit_current_amount,
            edit_deadline,
            edit_status,
            edit_milestones
        )
        st.success("Goal updated successfully!")
    
    # Milestone Chart
    st.subheader("Milestone Tracking")
    st.plotly_chart(
        get_milestone_chart(goal),
        use_container_width=True
    )
    
    # Delete Goal
    st.subheader("Delete Goal")
    delete_goal_index = st.number_input(
        "Enter goal index to delete", 
        min_value=0, 
        max_value=len(st.session_state.goals)-1,
        value=0,
        key="delete_goal_index"
    )
    
    if st.button("Delete Goal"):
        st.session_state.goals = delete_goal(delete_goal_index)
        st.success("Goal deleted successfully!")
else:
    st.info("No goals added yet. Add your first financial goal in the sidebar.")

# Investment Portfolio Section
st.header("Investment Portfolio")

# Portfolio Summary
st.subheader("Portfolio Summary")
portfolio_summary_chart, total_investment, total_current_value, total_return, return_percentage = get_portfolio_summary(st.session_state.portfolio)
st.plotly_chart(portfolio_summary_chart, use_container_width=True)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Invested", f"₹{total_investment:,.2f}")
with col2:
    st.metric("Current Value", f"₹{total_current_value:,.2f}")
with col3:
    st.metric("Total Return", f"₹{total_return:,.2f}")
with col4:
    st.metric("Return %", f"{return_percentage:.2f}%")

# Portfolio Distribution
st.subheader("Portfolio Distribution")
st.plotly_chart(
    get_portfolio_distribution(st.session_state.portfolio),
    use_container_width=True
)

# Portfolio Table
st.subheader("Your Investments")
if not st.session_state.portfolio.empty:
    st.dataframe(
        st.session_state.portfolio,
        use_container_width=True,
        hide_index=True
    )
    
    # Edit Investment
    st.subheader("Edit Investment")
    edit_investment_index = st.number_input(
        "Enter investment index to edit", 
        min_value=0, 
        max_value=len(st.session_state.portfolio)-1,
        value=0,
        key="edit_investment_index"
    )
    
    investment = st.session_state.portfolio.iloc[edit_investment_index]
    
    col1, col2 = st.columns(2)
    
    with col1:
        edit_investment_type = st.selectbox(
            "Investment Type",
            options=["Stocks", "Bonds", "Mutual Funds", "Crypto", "Other"],
            index=["Stocks", "Bonds", "Mutual Funds", "Crypto", "Other"].index(investment['investment_type']),
            key="edit_investment_type"
        )
        edit_investment_name = st.text_input(
            "Investment Name", 
            value=investment['name'],
            key="edit_investment_name"
        )
        edit_amount = st.number_input(
            "Amount Invested",
            min_value=0.01,
            value=float(investment['amount']),
            key="edit_investment_amount"
        )
    
    with col2:
        edit_purchase_date = st.date_input(
            "Purchase Date",
            value=pd.to_datetime(investment['purchase_date']),
            key="edit_investment_date"
        )
        edit_current_value = st.number_input(
            "Current Value",
            min_value=0.0,
            value=float(investment['current_value']),
            key="edit_investment_value"
        )
    
    if st.button("Update Investment"):
        st.session_state.portfolio = update_investment(
            edit_investment_index,
            edit_investment_type,
            edit_investment_name,
            edit_amount,
            edit_purchase_date,
            edit_current_value
        )
        st.success("Investment updated successfully!")
    
    # Delete Investment
    st.subheader("Delete Investment")
    delete_investment_index = st.number_input(
        "Enter investment index to delete", 
        min_value=0, 
        max_value=len(st.session_state.portfolio)-1,
        value=0,
        key="delete_investment_index"
    )
    
    if st.button("Delete Investment"):
        st.session_state.portfolio = delete_investment(delete_investment_index)
        st.success("Investment deleted successfully!")
else:
    st.info("No investments added yet. Add your first investment in the sidebar.")

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center'>
        <p>Made with ❤️ using Streamlit</p>
    </div>
""", unsafe_allow_html=True)