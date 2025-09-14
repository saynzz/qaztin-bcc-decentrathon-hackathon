def select_best_product(features):
    scores = {
        'Карта с кэшбэком': 0,
        'Депозит Накопительный': 0,
        'Кредитная карта': 0,
        'Кредит наличными': 0,
        'Карта для путешествий': 0,
        'Премиальная карта': 0,
        'Обмен валют': 0,
        'Инвестиции': 0
    }

    # 🎒 Тревел-карта
    if features.get('has_travel_signals') and features['total_transactions'] > 50:
        scores['Карта для путешествий'] += 12

    # 💸 Кредит наличными
    if features.get('has_credit_need') and features['std_transaction_amount'] > 5000:
        scores['Кредит наличными'] += 11

    # 👑 Премиальная карта
    if features.get('has_premium_signals') and features['avg_balance'] > 6_000_000:
        scores['Премиальная карта'] += 10

    # 🏦 Депозит
    if features['salary_detected'] and features['avg_transaction_amount'] < 7000:
        scores['Депозит Накопительный'] += 9
    if features['avg_balance'] > 500_000 and features['low_spending']:
        scores['Депозит Накопительный'] += 5

    # 💳 Кредитная карта
    if features['total_transfers'] > 20 and features['std_transaction_amount'] > 10000:
        scores['Кредитная карта'] += 8

    # 🛍️ Кэшбэк
    if features['total_transactions'] > 40:
        scores['Карта с кэшбэком'] += 7
    if 'магазин' in features['top_categories'].lower() or features.get('has_cashback_signals'):
        scores['Карта с кэшбэком'] += 5

    # 💱 Обмен валют
    if features.get('has_fx_transfers'):
        scores['Обмен валют'] += 6

    # 📈 Инвестиции
    if features.get('has_invest_signals'):
        scores['Инвестиции'] += 6

    # ✅ Финальный выбор
    best_product = max(scores, key=scores.get)
    return best_product, scores
