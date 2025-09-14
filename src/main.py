import os
import pandas as pd
from src.features import extract_features
from src.product_selector import select_best_product
from src.push_generator import generate_push

DATA_FOLDER = 'data'
OUTPUT_FILE = 'output/submission.csv'

def get_client_codes():
    return sorted(set([
        f.split('_')[1]
        for f in os.listdir(DATA_FOLDER)
        if f.endswith('.csv')
    ]))

def process_client(client_code):
    tx_file = f'{DATA_FOLDER}/client_{client_code}_transactions_3m.csv'
    tf_file = f'{DATA_FOLDER}/client_{client_code}_transfers_3m.csv'

    tx_df = pd.read_csv(tx_file)
    tf_df = pd.read_csv(tf_file)

    features = extract_features(tx_df, tf_df)
    product = select_best_product(features)
    push = generate_push(client_code, product, features, tone='friendly')

    return {
        'client_code': client_code,
        'product': product,
        'push_notification': push
    }

def main():
    results = []
    client_codes = get_client_codes()

    for code in client_codes:
        result = process_client(code)
        results.append(result)

    df = pd.DataFrame(results)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f'✅ Submission saved to {OUTPUT_FILE}')

if __name__ == '__main__':
    main()
