import streamlit as st
import pandas as pd
from src.features import extract_features
from src.product_selector import select_best_product
from src.push_generator import generate_push

DATA_FOLDER = 'data'

def load_client_data(client_code):
    tx = pd.read_csv(f'{DATA_FOLDER}/client_{client_code}_transactions_3m.csv')
    tf = pd.read_csv(f'{DATA_FOLDER}/client_{client_code}_transfers_3m.csv')
    return tx, tf

st.set_page_config(page_title="QazFinance Push Generator", layout="wide")

st.sidebar.image("assets/logo.png", width=150)
st.sidebar.title("QazFinance")
st.sidebar.markdown("Персонализированные рекомендации на основе транзакций")

st.title("📲 Push-уведомления для клиентов банка")

client_code = st.selectbox("Выберите клиента", options=[58, 59, 60])

tx_df, tf_df = load_client_data(client_code)
features = extract_features(tx_df, tf_df)
product = select_best_product(features)
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

    st.subheader("💬 Push-сообщение")
    st.markdown(f"""
        <div style='background:#f0f8ff;padding:15px;border-radius:10px;font-size:16px'>
        {push}
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.caption("© QazFinance · Хакатон BCC · Сделано с кайфом 💙")
