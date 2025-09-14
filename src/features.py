import pandas as pd

def extract_features(transactions_df, transfers_df):
    features = {}

    # Очистка названий колонок от пробелов
    transactions_df.columns = transactions_df.columns.str.strip()
    transfers_df.columns = transfers_df.columns.str.strip()

    # Общая активность
    features['total_transactions'] = len(transactions_df)
    features['total_transfers'] = len(transfers_df)

    # Средний чек
    if 'amount' in transactions_df.columns:
        features['avg_transaction_amount'] = transactions_df['amount'].mean()
        features['std_transaction_amount'] = transactions_df['amount'].std()
    else:
        features['avg_transaction_amount'] = 0
        features['std_transaction_amount'] = 0

    # Категории
    if 'category' in transactions_df.columns:
        top_categories = transactions_df['category'].value_counts().head(3).index.tolist()
        features['top_categories'] = ', '.join(top_categories)
    else:
        features['top_categories'] = 'unknown'

    # Зарплата (по ключевым словам)
    salary_keywords = ['salary', 'зарплата', 'payroll']
    possible_cols = ['description', 'Назначение', 'details', 'message', 'comment']
    salary_column = next((col for col in possible_cols if col in transactions_df.columns), None)

    if salary_column:
        salary_tx = transactions_df[
            transactions_df[salary_column].astype(str).str.lower().str.contains('|'.join(salary_keywords))
        ]
        features['salary_detected'] = int(len(salary_tx) > 0)
    else:
        features['salary_detected'] = 0

    # Регулярные платежи
    recurring_column = next((col for col in possible_cols if col in transactions_df.columns), None)
    if recurring_column:
        recurring = transactions_df[recurring_column].value_counts().loc[lambda x: x > 2].index.tolist()
        features['recurring_payments'] = len(recurring)
    else:
        features['recurring_payments'] = 0

    return features
