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
```

---

### STEP 4. Streamlit Cloud で公開

ここが最後の仕上げです。サーバーを立ち上げます。

1.  **Streamlit Community Cloud** ( [https://streamlit.io/cloud](https://streamlit.io/cloud) ) にアクセスし、GitHubアカウントでログインします。
2.  「New app」をクリック。
3.  STEP 3で作ったリポジトリ（`nurse-app`）、ブランチ（`main`）、ファイル名（`streamlit_app.py`）を選択します。
4.  **まだ「Deploy」を押さないでください！** 「Advanced settings」をクリックします。
5.  **Secrets** 欄に、STEP 1でダウンロードしたJSONの中身と、スプレッドシートのURL、パスワードを貼り付けます。以下の形式に従ってください。

```toml
# Secrets 欄にコピペする内容

# アプリのログインパスワード
PASSWORD = "hospital1234"

# スプレッドシートの接続情報
[connections.gsheets]
spreadsheet = "https://docs.google.com/spreadsheets/d/あなたのスプレッドシートID/edit"

# 以下、STEP1でDLしたJSONの中身を貼り付け
type = "service_account"
project_id = "..."
private_key_id = "..."
private_key = "-----BEGIN PRIVATE KEY-----..."
client_email = "..."
client_id = "..."
auth_uri = "..."
token_uri = "..."
auth_provider_x509_cert_url = "..."
client_x509_cert_url = "..."
