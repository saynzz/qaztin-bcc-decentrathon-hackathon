import streamlit as st
import pandas as pd
import os
import io
import plotly.express as px
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

def generate_submission(client_codes):
    results = []

    for code in client_codes:
        tx_df, tf_df = load_client_data(code)
        if tx_df is None or tf_df is None:
            continue

        features = extract_features(tx_df, tf_df)
        product, scores = select_best_product(features)
        push = generate_push(code, product, features, tone='friendly')

        results.append({
            "client_code": code,
            "product": product,
            "push_notification": push,
            "top_categories": features.get("top_categories", ""),
            "avg_transaction_amount": round(features.get("avg_transaction_amount", 0), 2),
            "score_" + product: scores.get(product, 0)
        })

    return pd.DataFrame(results)

st.set_page_config(page_title="QazFinance Push Generator", layout="wide")

st.sidebar.image("assets/logo.png", width=150)
st.sidebar.title("QazTin")
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

    if 'category' in tx_df.columns:
        st.subheader("📊 График расходов по категориям")
        category_summary = tx_df.groupby('category')['amount'].sum().reset_index()
        fig_cat = px.bar(category_summary, x='category', y='amount',
                         title='Сумма расходов по категориям',
                         labels={'amount': 'Сумма (₸)', 'category': 'Категория'},
                         text_auto='.2s')
        fig_cat.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_cat, use_container_width=True)

    st.subheader("🔁 Переводы")
    st.dataframe(tf_df)

    if 'date' in tf_df.columns:
        st.subheader("📈 Активность переводов по дням")
        tf_df['date'] = pd.to_datetime(tf_df['date'])
        transfers_by_day = tf_df.groupby(tf_df['date'].dt.date)['amount'].sum().reset_index()
        fig_tf = px.line(transfers_by_day, x='date', y='amount',
                         title='Сумма переводов по дням',
                         labels={'amount': 'Сумма (₸)', 'date': 'Дата'})
        st.plotly_chart(fig_tf, use_container_width=True)

    if 'avg_balance' in features and features['avg_balance'] > 0:
        st.subheader("💰 Средний остаток")
        st.metric(label="Средний остаток на счёте", value=f"{int(features['avg_balance']):,} ₸")

with col2:
    st.subheader("🧠 Фичи")
    st.json(features)

    st.subheader("🎯 Продукт")
    st.success(product)

    st.subheader("📊 Баллы по продуктам")
    scores_table = pd.DataFrame.from_dict(scores, orient='index', columns=['Баллы']).sort_values(by='Баллы', ascending=False)
    st.table(scores_table)

    st.subheader("📱 Push-превью (мобильный стиль)")
    st.markdown(f"""
    <div style='background:#1e1e1e;padding:20px;border-radius:20px;width:100%;max-width:400px;margin:auto;color:white;font-family:sans-serif'>
        <div style='display:flex;align-items:center;margin-bottom:10px'>
            <img src='https://upload.wikimedia.org/wikipedia/commons/thumb/5/5f/Qazkom_Logo.svg/2560px-Qazkom_Logo.svg.png' width='24' style='margin-right:10px;border-radius:4px'>
            <span style='font-weight:bold'>QazFinance</span>
        </div>
        <div style='background:#2e2e2e;padding:15px;border-radius:10px;font-size:15px;line-height:1.4'>
            {push}
        </div>
        <div style='margin-top:12px;display:flex;justify-content:space-between'>
            <button style='background:#007aff;border:none;color:white;padding:8px 16px;border-radius:8px;font-size:14px'>Оформить</button>
            <button style='background:#444;border:none;color:white;padding:8px 16px;border-radius:8px;font-size:14px'>Позже</button>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("### 📤 Генерация push-сообщений по всем клиентам")

if st.button("Сгенерировать для всех"):
    submission_df = generate_submission(client_codes)

    if submission_df.empty:
        st.error("🚫 Не удалось сгенерировать CSV — нет данных.")
    else:
        st.subheader("📋 Предпросмотр push-сообщений")
        st.dataframe(submission_df)

        csv_buffer = io.StringIO()
        submission_df.to_csv(csv_buffer, index=False)
        st.download_button(
            label="📥 Скачать submission.csv",
            data=csv_buffer.getvalue(),
            file_name="submission.csv",
            mime="text/csv"
        )

st.markdown("---")
st.caption("© QazTin · Хакатон BCC · Сделано с кайфом 💙")
