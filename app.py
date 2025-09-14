import streamlit as st
import pandas as pd
import os
from src.features import extract_features
from src.product_selector import select_best_product
from src.push_generator import generate_push

DATA_FOLDER = 'data'

def get_client_codes():
    files = os.listdir(DATA_FOLDER)
    codes = set()
    for f in files:
        if f.endswith('_transactions_3m.csv'):
            parts = f.split('_')
            if len(parts) >= 3:
                codes.add(parts[1])
    return sorted(codes)

def load_client_data(client_code):
    tx_path = f'{DATA_FOLDER}/client_{client_code}_transactions_3m.csv'
    tf_path = f'{DATA_FOLDER}/client_{client_code}_transfers_3m.csv'

    if not os.path.exists(tx_path) or not os.path.exists(tf_path):
        return None, None

    tx = pd.read_csv(tx_path)
    tf = pd.read_csv(tf_path)

    tx.columns = tx.columns.str.strip()
    tf.columns = tf.columns.str.strip()

    return tx, tf

st.set_page_config(page_title="QazFinance Push Generator", layout="wide")

st.sidebar.image("assets/logo.png", width=150)
st.sidebar.title("QazFinance")
st.sidebar.markdown("Персонализированные рекомендации на основе транзакций")

st.title("📲 Push-уведомления для клиентов банка")

client_codes = get_client_codes()
if not client_codes:
    st.warning("Нет доступных клиентов в папке data/")
    st.stop()

client_code = st.selectbox("Выберите клиента", options=client_codes)

tx_df, tf_df = load_client_data(client_code)
if tx_df is None or tf_df is None:
    st.error(f"Файлы для клиента {client_code} не найдены.")
    st.stop()

features = extract_features(tx_df, tf_df)
product, scores = select_best_product(features)
push = generate_push(client_code, product, features, tone='friendly')

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📊 Транзакции")
    st.dataframe(tx_df)

    st.subheader("🔁 Переводы")
    st.dataframe(tf_df)

with col2:
    st.subheader("🧠 Фичи")
    st.json(features)

    st.subheader("🎯 Продукт")
    st.success(product)

    st.subheader("📊 Баллы по продуктам")
    scores_table = pd.DataFrame.from_dict(scores, orient='index', columns=['Баллы']).sort_values(by='Баллы', ascending=False)
    st.table(scores_table)

    st.subheader("💬 Push-сообщение")
    st.markdown(f"""
        <div style='background:#f0f8ff;padding:15px;border-radius:10px;font-size:16px'>
        {push}
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.caption("© QazTin · Хакатон BCC · Сделано с кайфом 💙")
