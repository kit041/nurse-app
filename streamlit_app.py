import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- 設定 ---
st.set_page_config(page_title="Myポートフォリオ", layout="centered")

# --- パスワード認証（簡易） ---
# 実際の運用では st.secrets にパスワードを設定してください
if "auth" not in st.session_state:
    st.session_state.auth = False

def check_password():
    password = st.text_input("パスワードを入力", type="password")
    if st.button("ログイン"):
        # 簡易パスワード: hospital1234
        if password == st.secrets["PASSWORD"]:
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("パスワードが違います")

if not st.session_state.auth:
    check_password()
    st.stop()

# --- データ接続 ---
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    # キャッシュを使わず常に最新を取得 (ttl=0)
    return conn.read(worksheet="data", ttl=0)

def save_record(name, category, item_id, level, comment):
    df = load_data()
    new_data = pd.DataFrame([{
        "nurse_name": name,
        "category": category,
        "item_id": item_id,
        "level": level,
        "comment": comment,
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }])
    updated_df = pd.concat([df, new_data], ignore_index=True)
    conn.update(worksheet="data", data=updated_df)

# --- UI構築 ---
st.title("🏥 Myポートフォリオ")

# ユーザー選択（実際はログインID等で自動化推奨）
user_name = st.selectbox("名前を選択", ["新人A", "新人B", "新人C"])

# 入力フォーム
with st.form("input_form"):
    category = st.selectbox("カテゴリ", ["I.基本姿勢", "II.看護技術", "III.管理的側面"])
    item_id = st.text_input("項目名", placeholder="例: 採血")
    
    level = st.radio("到達度", [1, 2, 3, 4], 
                     format_func=lambda x: f"Level {x}", horizontal=True)
    
    comment = st.text_area("振り返り")
    
    submitted = st.form_submit_button("記録する")
    
    if submitted:
        save_record(user_name, category, item_id, level, comment)
        st.success("保存しました！")
        st.balloons()

# 履歴表示
st.divider()
st.subheader("最近の記録")
df = load_data()
my_df = df[df["nurse_name"] == user_name].tail(5) # 最新5件
st.dataframe(my_df)
