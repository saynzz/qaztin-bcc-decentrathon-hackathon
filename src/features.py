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

    # Остаток (если есть)
    features['avg_balance'] = transactions_df['balance'].mean() if 'balance' in transactions_df.columns else 0

    # Категории
    if 'category' in transactions_df.columns:
        top_categories = transactions_df['category'].value_counts().head(3).index.tolist()
        features['top_categories'] = ', '.join(top_categories)

        def has_many(cat):
            return transactions_df['category'].value_counts().get(cat, 0) >= 3

        features['has_travel_signals'] = any(has_many(c) for c in ['Такси', 'Отели', 'Путешествия'])
        features['has_premium_signals'] = features['avg_balance'] > 6_000_000 or has_many('Ювелирные украшения')
        features['has_cashback_signals'] = 'Кафе и рестораны' in top_categories
    else:
        features['top_categories'] = 'unknown'
        features['has_travel_signals'] = False
        features['has_premium_signals'] = False
        features['has_cashback_signals'] = False

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

    # FX / инвестиции / кредиты
    if 'type' in transfers_df.columns:
        types = transfers_df['type'].astype(str).str.lower()
        features['has_fx_transfers'] = types.str.contains('fx').any()
        features['has_invest_signals'] = types.str.contains('invest').any()
        features['has_credit_need'] = types.str.contains('loan|installment|atm').any()
    else:
        features['has_fx_transfers'] = False
        features['has_invest_signals'] = False
        features['has_credit_need'] = False

    # Низкие траты → сигнал на депозит
    features['low_spending'] = features['avg_transaction_amount'] < 3000

    return features
