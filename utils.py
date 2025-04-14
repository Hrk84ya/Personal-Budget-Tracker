import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import io

def load_transactions():
    if not os.path.exists('data/transactions.csv'):
        df = pd.DataFrame(columns=['date', 'type', 'category', 'amount', 'description', 'tags'])
        df.to_csv('data/transactions.csv', index=False)
    return pd.read_csv('data/transactions.csv')

def save_transaction(date, trans_type, category, amount, description, tags=""):
    df = load_transactions()
    new_transaction = pd.DataFrame({
        'date': [date],
        'type': [trans_type],
        'category': [category],
        'amount': [amount],
        'description': [description],
        'tags': [tags]
    })
    df = pd.concat([df, new_transaction], ignore_index=True)
    df.to_csv('data/transactions.csv', index=False)
    return df

def edit_transaction(index, date, trans_type, category, amount, description, tags):
    df = load_transactions()
    df.loc[index, 'date'] = date
    df.loc[index, 'type'] = trans_type
    df.loc[index, 'category'] = category
    df.loc[index, 'amount'] = amount
    df.loc[index, 'description'] = description
    df.loc[index, 'tags'] = tags
    df.to_csv('data/transactions.csv', index=False)
    return df

def delete_transaction(index):
    df = load_transactions()
    df = df.drop(index).reset_index(drop=True)
    df.to_csv('data/transactions.csv', index=False)
    return df

def search_transactions(df, search_term, start_date=None, end_date=None, 
                       transaction_type=None, category=None, min_amount=None, 
                       max_amount=None, tags=None):
    # Convert date column to datetime if it's not already
    df['date'] = pd.to_datetime(df['date'])
    
    # Create a mask for each filter
    mask = pd.Series(True, index=df.index)
    
    # Search term filter (searches in description and tags)
    if search_term:
        mask &= (df['description'].str.contains(search_term, case=False, na=False) |
                df['tags'].str.contains(search_term, case=False, na=False))
    
    # Date range filter
    if start_date:
        mask &= df['date'] >= pd.to_datetime(start_date)
    if end_date:
        mask &= df['date'] <= pd.to_datetime(end_date)
    
    # Transaction type filter
    if transaction_type:
        mask &= df['type'] == transaction_type
    
    # Category filter
    if category:
        mask &= df['category'] == category
    
    # Amount range filter
    if min_amount is not None:
        mask &= df['amount'] >= min_amount
    if max_amount is not None:
        mask &= df['amount'] <= max_amount
    
    # Tags filter
    if tags:
        mask &= df['tags'].str.contains(tags, case=False, na=False)
    
    return df[mask]

def get_all_tags(df):
    # Get all unique tags from the transactions
    all_tags = set()
    for tags in df['tags'].dropna():
        all_tags.update(tag.strip() for tag in tags.split(','))
    return sorted(list(all_tags))

def get_category_distribution(df):
    # Filter for expenses only and handle empty dataframe
    expense_data = df[df['type'] == 'Expense'].copy()
    if expense_data.empty:
        return create_empty_chart("No expense data available")
    
    # Calculate category totals
    category_totals = expense_data.groupby('category')['amount'].sum().reset_index()
    
    # Create pie chart
    fig = px.pie(
        category_totals,
        values='amount',
        names='category',
        title='Spending by Category',
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    # Update layout
    fig.update_layout(
        height=400,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

def get_monthly_trends(df):
    # Convert date to datetime if it's not already
    df['date'] = pd.to_datetime(df['date'])
    
    # Group by month and type
    monthly_totals = df.groupby([
        df['date'].dt.strftime('%Y-%m'),
        'type'
    ])['amount'].sum().reset_index()
    
    if monthly_totals.empty:
        return create_empty_chart("No transaction data available")
    
    # Create bar chart
    fig = px.bar(
        monthly_totals,
        x='date',
        y='amount',
        color='type',
        title='Monthly Income vs Expenses',
        barmode='group',
        color_discrete_sequence=['#2ECC71', '#E74C3C']
    )
    
    # Update layout
    fig.update_layout(
        height=400,
        xaxis_title="Month",
        yaxis_title="Amount (₹)",
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

def create_empty_chart(message):
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        xref="paper",
        yref="paper",
        showarrow=False,
        font=dict(size=14)
    )
    fig.update_layout(
        height=400,
        xaxis=dict(showgrid=False, showticklabels=False),
        yaxis=dict(showgrid=False, showticklabels=False)
    )
    return fig

def get_monthly_summary(df):
    df['date'] = pd.to_datetime(df['date'])
    current_month = datetime.now().strftime('%Y-%m')
    month_data = df[df['date'].dt.strftime('%Y-%m') == current_month]

    income = month_data[month_data['type'] == 'Income']['amount'].sum()
    expenses = month_data[month_data['type'] == 'Expense']['amount'].sum()
    balance = income - expenses

    return income, expenses, balance

def export_to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Transactions')
    return output.getvalue()

def export_to_csv(df):
    output = io.StringIO()
    df.to_csv(output, index=False)
    return output.getvalue()

def load_budgets():
    if not os.path.exists('data/budgets.csv'):
        df = pd.DataFrame(columns=['category', 'monthly_limit'])
        df.to_csv('data/budgets.csv', index=False)
    return pd.read_csv('data/budgets.csv')

def save_budget(category, monthly_limit):
    df = load_budgets()
    df.loc[df['category'] == category, 'monthly_limit'] = monthly_limit
    df.to_csv('data/budgets.csv', index=False)
    return df

def get_budget_status(df, budgets):
    df['date'] = pd.to_datetime(df['date'])
    current_month = datetime.now().strftime('%Y-%m')
    month_data = df[df['date'].dt.strftime('%Y-%m') == current_month]
    
    # Calculate actual spending by category
    actual_spending = month_data[month_data['type'] == 'Expense'].groupby('category')['amount'].sum().reset_index()
    
    # Merge with budgets
    budget_status = pd.merge(budgets, actual_spending, on='category', how='left')
    budget_status['amount'] = budget_status['amount'].fillna(0)
    budget_status['percentage'] = (budget_status['amount'] / budget_status['monthly_limit'] * 100).fillna(0)
    budget_status['status'] = budget_status.apply(
        lambda x: 'Over Budget' if x['percentage'] > 100 else 
                 'Warning' if x['percentage'] > 80 else 
                 'Good', axis=1
    )
    
    return budget_status

def get_budget_vs_actual_chart(df, budgets):
    budget_status = get_budget_status(df, budgets)
    
    fig = go.Figure()
    
    # Add budget bars
    fig.add_trace(go.Bar(
        name='Budget Limit',
        x=budget_status['category'],
        y=budget_status['monthly_limit'],
        marker_color='lightblue'
    ))
    
    # Add actual spending bars
    fig.add_trace(go.Bar(
        name='Actual Spending',
        x=budget_status['category'],
        y=budget_status['amount'],
        marker_color='lightgreen'
    ))
    
    fig.update_layout(
        title='Budget vs Actual Spending by Category',
        barmode='group',
        xaxis_tickangle=-45,
        height=500
    )
    
    return fig

def check_budget_alerts(df, budgets):
    budget_status = get_budget_status(df, budgets)
    alerts = []
    
    for _, row in budget_status.iterrows():
        if row['percentage'] > 100:
            alerts.append(f"⚠️ {row['category']} is over budget by ₹{row['amount'] - row['monthly_limit']:,.2f}")
        elif row['percentage'] > 80:
            alerts.append(f"⚠️ {row['category']} is approaching budget limit ({(row['percentage']):.1f}% used)")
    
    return alerts