def select_best_product(features):
    scores = {
        'cashback_card': 0,
        'deposit': 0,
        'credit_card': 0
    }

    # Кэшбэк — если много покупок
    if features['total_transactions'] > 30:
        scores['cashback_card'] += 10
    if 'магазин' in features['top_categories']:
        scores['cashback_card'] += 5

    # Депозит — если есть остатки и зарплата
    if features['salary_detected'] and features['avg_transaction_amount'] < 10000:
        scores['deposit'] += 10

    # Кредит — если много переводов и нестабильные траты
    if features['total_transfers'] > 10 and features['std_transaction_amount'] > 15000:
        scores['credit_card'] += 10

    return max(scores, key=scores.get)
