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

### STEP 4. Streamlit Cloud で公開

#1.  **Streamlit Community Cloud** ( [https://streamlit.io/cloud](https://streamlit.io/cloud) ) にアクセスし、GitHubアカウントでログインします。
#2.  「New app」をクリック。
#3.  STEP 3で作ったリポジトリ（`nurse-app`）、ブランチ（`main`）、ファイル名（`streamlit_app.py`）を選択します。
#4.  **まだ「Deploy」を押さないでください！** 「Advanced settings」をクリックします。
#5.  **Secrets** 欄に、STEP 1でダウンロードしたJSONの中身と、スプレッドシートのURL、パスワードを貼り付けます。以下の形式に従ってください。

#```toml
# Secrets 欄にコピペする内容

# アプリのログインパスワード
PASSWORD = "hospital1234"

# スプレッドシートの接続情報
[connections.gsheets]
spreadsheet = "https://docs.google.com/spreadsheets/d/1DjvdkaTVntzMPGY7UH4v3Emq9V6OCgk0XaXDx8Im_FM/edit"

# 以下、STEP1でDLしたJSONの中身を貼り付け
type = "service_account",
project_id = "nurse-app-2026-486903",
private_key_id = "b039e47a02f3d4c14cff4a53cc235c7636e85a39",
private_key = "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDA9C1LMy2J9rFl\nI8HUXKBsT1zxtIEBsQLJ3qcG+Xz1LTORkrUG3EitwlOi7QO+KXU1FbNYdcXl/l3E\n98NF9HaW6lVpxt/tC/nsRXLfpClOhY8GLG5wimvR0zJIBSwWQM3vBatouNRtP9LH\nLHKIFF3bEUs51w43pTMgd+YjAjR98Pq9ubutqyQyr7uanPSGVmzq2GMBefAPUIaR\nSBKeWPapo3r+p6USSiAm+8/n6XTIlB934IUoeyRRh/5LAdTpWVYgXl7b1WJMJuZR\ntaSZ07Hp2r8jyhQKrLVUqsBBB7w5J0s2bl8WHa22MrQW6qOl6eXs1eF6HfLxQf3K\n3eDTS7BNAgMBAAECggEAPe5hl1Bu3mhS2d6XOP0d9IWolF/WRF+3QGn5fFCZnewL\nMD9BYVlU7oh/5bxjRibyWr6DWPI8OaziFfVcNNjZM2k1TwUpHGGKrx4/V67OH0jY\n9idOr0qOfsNl0R3v35ifQIe2U593dzVUBt+qRykaUtUDKyZuhse8WECDmlr71Cvz\n2NnBfmm3jGmXbWQ2iKBGjbhOHCAhWXQ9xDkKqiJ8lgrqZEsckAROQp2538v1WSIz\nI6r46TLR7YGDqOVcv13+u3MZxN9rS5nQyWCFHAgx1dhn7MA0X1v/IeHK23CoMlF+\nxtvW8KDW8FttBez10k0iwC5ufyv1kk5ldNHhMHrbdQKBgQD7pAEwXegKkekw7HlU\nHkBMT2mxkouPtq+DxizdpK3nJvvEcFj3ptgWkJo4IdFUa7EBNprXZMQUTV1IHtAQ\npIqRucbbo0zRuIoIBV/pPmWTBNcOUREgCQ4g17CX/MvipuzB5H0EsHhns9Y6pFqt\nBaUEibjXM5qC6qlXTz28B/AwYwKBgQDES+dGBkzd/hUs32JXKxd8/buWIV4a6HxQ\nqjAwkUhZ/2fZz3XeAGXmgHBDn2teZ8XYdeUNdOd5W4TkBmGfzEoWJ5nYupsu38Kj\n0WykdVMavnsL7WLDKRU4pCdoxAbXSJQSRFdXfq6vsVob15+z2FNTZ+TkCqFqeRHL\nmXA94oqDjwKBgE1dlfP92xps08nz2jWPe2s6ux8aFAhiPUIBSsf2GnVH2f4CIIg7\nZpJBcPizBP20gl4CIMb6NwKa6oQC3StQuz2kZUwfv712xBFFPcCjK21w/oFrUR2N\nSyezyJph4XlUotPV4M3xR4Nymfm7kBlD9AEaKpcXSXjYlqm+Nhe6RRFLAoGAaFsV\n67NDwCzo4v8rD75X8VoPFQROPC3mkRe5IMjL1xSiCDhzp/88LSuRA1JISVsP4kDi\n8aF5wZm272a5FbQMmvSYpJCoGWZZ2q9me5PoB2rGjZO5EpnPr1oNnXPBU0hBd+if\nKmOtyLeXeP/L5leWDNxJ4jYIlEsi+8Np2WyLSN8CgYEAmYceIRRMYvRwXT9EckJ2\nqBzcH/70BWNRGp4n64SWAa90jkZel8fDfvc6LE1X7tr1skVs+buT4a9N6/+ZaSLZ\n0efkUEtT7Y65jn7oz6BaRcJm3qowFl5xIBr1cBtq47zK4j+uMtL5yr5DHe2gS8Cy\n6BFiKJSXovNrxEthmVSm4h4=\n-----END PRIVATE KEY-----\n",
client_email = "streamlit-bot@nurse-app-2026-486903.iam.gserviceaccount.com",
client_id = "101960249219821659242",
auth_uri = "https://accounts.google.com/o/oauth2/auth",
token_uri = "https://oauth2.googleapis.com/token",
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs",
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/streamlit-bot%40nurse-app-2026-486903.iam.gserviceaccount.com",
