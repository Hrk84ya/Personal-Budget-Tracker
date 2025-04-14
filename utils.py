import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import io

def load_transactions():
    if not os.path.exists('data/transactions.csv'):
        df = pd.DataFrame(columns=['date', 'type', 'category', 'amount', 'description'])
        df.to_csv('data/transactions.csv', index=False)
    return pd.read_csv('data/transactions.csv')

def save_transaction(date, trans_type, category, amount, description):
    df = load_transactions()
    new_transaction = pd.DataFrame({
        'date': [date],
        'type': [trans_type],
        'category': [category],
        'amount': [amount],
        'description': [description]
    })
    df = pd.concat([df, new_transaction], ignore_index=True)
    df.to_csv('data/transactions.csv', index=False)
    return df

def get_category_distribution(df):
    category_totals = df.groupby('category')['amount'].sum().reset_index()
    fig = px.pie(
        category_totals,
        values='amount',
        names='category',
        title='Spending by Category',
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    return fig

def get_monthly_trends(df):
    df['date'] = pd.to_datetime(df['date'])
    monthly_totals = df.groupby([df['date'].dt.strftime('%Y-%m'), 'type'])['amount'].sum().reset_index()
    fig = px.bar(
        monthly_totals,
        x='date',
        y='amount',
        color='type',
        title='Monthly Income vs Expenses',
        barmode='group',
        color_discrete_sequence=['#2ECC71', '#E74C3C']
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