def generate_push(client_code, product, features, tone='friendly'):
    if tone == 'friendly':
        return f"Привет, {client_code}! Мы заметили, что вы часто тратите на {features['top_categories']}. Карта с кэшбэком может вернуть вам часть этих расходов!"
    elif tone == 'smart':
        return f"Анализ ваших транзакций показал, что депозит принес бы вам больше выгоды. Проверьте наши условия!"
    elif tone == 'business':
        return f"{client_code}, на основе ваших финансовых операций мы рекомендуем продукт: {product}. Он поможет оптимизировать ваши расходы."
    else:
        return f"{client_code}, вам может подойти продукт: {product}."
