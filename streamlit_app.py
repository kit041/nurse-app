import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- 1. ページ設定 (最上部に必須) ---
st.set_page_config(page_title="Staff MyPage", layout="centered")

# --- 2. CSSスタイル調整 (スマホで見やすく) ---
st.markdown("""
<style>
    /* ボタンのスタイル調整 */
    div.stButton > button {
        width: 100%;
        padding-top: 10px;
        padding-bottom: 10px;
        font-weight: bold;
        border-radius: 8px;
    }
    /* 大きな文字クラス */
    .big-font {
        font-size: 20px !important;
        font-weight: bold;
        margin-bottom: 10px;
        display: block;
    }
    /* プログレスバーの色変更 */
    .stProgress > div > div > div > div {
        background-color: #4CAF50;
    }
    /* エキスパンダーのヘッダー調整 */
    .streamlit-expanderHeader {
        font-weight: bold;
        background-color: #f8f9fa;
        border-radius: 5px;
    }
    /* タブのフォント調整 */
    button[data-baseweb="tab"] {
        font-size: 16px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. マスタデータ定義 (評価項目リスト) ---
# 院内の教育基準に合わせてここを自由に編集してください
GUIDELINE_ITEMS = {
    "I. 態度": [
        {"id": "ethic_1", "title": "倫理的感性", "desc": "守秘義務を守り、患者のプライバシーに配慮できる"},
        {"id": "comm_1",  "title": "報告・連絡・相談", "desc": "適切なタイミングで報告・連絡・相談ができる"},
        {"id": "resp_1",  "title": "責任意識", "desc": "自己の課題を認識し、主体的に学習に取り組む"}
    ],
    "II. 技術": [
        {"id": "tech_1", "title": "感染予防（手洗い）", "desc": "正しい手順で衛生的手洗い・手指消毒ができる"},
        {"id": "tech_2", "title": "バイタルサイン", "desc": "正確に測定し、異常値を報告できる"},
        {"id": "tech_3", "title": "採血・静脈路確保", "desc": "安全に実施でき、合併症の兆候を観察できる"},
        {"id": "tech_4", "title": "吸引", "desc": "口腔・鼻腔吸引を安全に実施できる"},
        {"id": "tech_5", "title": "与薬（内服）", "desc": "6Rを確認し、誤薬なく与薬できる"}
    ],
    "III. 管理": [
        {"id": "safe_1", "title": "医療安全", "desc": "インシデントレポートの目的を理解し、記述できる"},
        {"id": "cost_1", "title": "コスト意識", "desc": "医療材料を適切に使用できる"}
    ]
}

# --- 4. パスワード認証 ---
if "auth" not in st.session_state:
    st.session_state.auth = False

def check_password():
    st.write("### 🔐 ログイン")
    password = st.text_input("パスワードを入力してください", type="password")
    if st.button("ログイン"):
        # Secretsにパスワードが設定されていればそれを使い、なければ"hospital1234"
        secret_pass = st.secrets.get("PASSWORD", "hospital1234")
        if password == secret_pass:
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("パスワードが違います")

if not st.session_state.auth:
    check_password()
    st.stop()

# --- 5. データ接続 & 関数 ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception:
    st.error("データベース接続設定(Secrets)を確認してください。")
    st.stop()

def load_data():
    """スプレッドシートからデータを取得"""
    try:
        # シート名 'data' から全データを取得 (ttl=0 でキャッシュ無効化)
        return conn.read(worksheet="data", ttl=0)
    except Exception:
        # シートが存在しない、または空の場合のエラー回避用ダミーデータ
        return pd.DataFrame(columns=["nurse_name", "category", "item_id", "level", "comment", "updated_at"])

def save_record(name, category, item_id, title, level, comment):
    """データを保存"""
    df = load_data()
    
    new_row = pd.DataFrame([{
        "nurse_name": name,
        "category": category,
        "item_id": item_id,
        "item_title": title,
        "level": level,
        "comment": comment,
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }])
    
    if df.empty:
        updated_df = new_row
    else:
        updated_df = pd.concat([df, new_row], ignore_index=True)
        
    conn.update(worksheet="data", data=updated_df)

# --- 6. ユーザー選択 (サイドバー) ---
st.sidebar.header("設定")
# 本来はログインIDに紐づけますが、デモとして選択式にします
user_name = st.sidebar.selectbox("ユーザー切替", ["新人A", "新人B", "新人C"])


# --- 7. アプリ本体 UI ---

# データの準備：現在のユーザーの最新状態を取得
df = load_data()
user_progress = {} # {item_id: level} の辞書を作る

if not df.empty and "nurse_name" in df.columns:
    # このユーザーのデータのみ抽出
    my_df = df[df["nurse_name"] == user_name]
    
    if not my_df.empty:
        # 日付でソートして、重複排除（最新の状態を取得）
        my_df = my_df.sort_values("updated_at")
        for _, row in my_df.iterrows():
            # item_idごとの最新レベルを辞書に保存
            user_progress[row["item_id"]] = int(row["level"])

# 進捗率の計算 (レベル3以上を「自立」とする)
all_items_count = sum(len(items) for items in GUIDELINE_ITEMS.values())
cleared_count = sum(1 for lvl in user_progress.values() if lvl >= 3)
progress_rate = cleared_count / all_items_count if all_items_count > 0 else 0

# --- 画面描画開始 ---

st.write(f"👋 お疲れ様です、**{user_name}** さん")

# 進捗バー表示
st.write("**今の自立度 (Lv3以上)**")
st.progress(progress_rate)
remaining = all_items_count - cleared_count
if remaining == 0:
    st.caption(f"🎉 おめでとうございます！ 全{all_items_count}項目で自立レベル達成です！")
else:
    st.caption(f"全{all_items_count}項目中、**{cleared_count}項目** 達成。あと **{remaining}項目** です！")

st.divider()

st.markdown('<p class="big-font">📌 今日の振り返り入力</p>', unsafe_allow_html=True)

# タブの作成
tab_names = list(GUIDELINE_ITEMS.keys())
tabs = st.tabs(tab_names)

# 各カテゴリの描画ループ
for i, (category, items) in enumerate(GUIDELINE_ITEMS.items()):
    with tabs[i]:
        # 未入力数をカウントして表示
        pending_count = sum(1 for item in items if user_progress.get(item["id"], 0) < 3)
        
        if pending_count > 0:
            st.info(f"💡 このカテゴリには、未達成が **{pending_count}件** あります")
        else:
            st.success("🎉 このカテゴリはすべて自立レベルです！")

        # 各項目のアコーディオン生成
        for item in items:
            current_level = user_progress.get(item["id"], 0)
            is_completed = current_level >= 3
            
            # アイコンとタイトルの決定
            icon = "✅" if is_completed else "📝"
            title_text = f"{icon} {item['title']}"
            if is_completed:
                title_text += " (Lv3達成済)"
            
            # アコーディオン (未達成ならデフォルトで開く、達成済みは閉じる)
            with st.expander(title_text, expanded=(not is_completed)):
                st.caption(f"**到達目標:** {item['desc']}")
                
                # ガイドライン参照ボタン（ヘルプ）
                if st.checkbox("詳しい評価基準を見る", key=f"help_{item['id']}"):
                    st.warning("Lv3基準： 安全安楽に実施でき、合併症の徴候を観察できること")

                # 入力フォーム
                # フォームキーを一意にする必要があります
                with st.form(key=f"form_{user_name}_{item['id']}"):
                    # レベル選択
                    level_options = [0, 1, 2, 3, 4]
                    level_labels = ["未実施", "Lv1: 見学", "Lv2: 実施(介助有)", "Lv3: 自立(OK)", "Lv4: 指導可"]
                    
                    # 現在のレベルが選択肢にあるか確認（念のため）
                    default_idx = current_level if current_level in level_options else 0

                    new_level = st.radio(
                        "今日の成果",
                        level_options,
                        format_func=lambda x: level_labels[x],
                        index=default_idx,
                        key=f"radio_{item['id']}"
                    )
                    
                    comment = st.text_area(
                        "振り返り・メモ",
                        placeholder="例：手順通りできたが、時間がかかった。",
                        key=f"comment_{item['id']}"
                    )
                    
                    # 送信ボタン
                    submitted = st.form_submit_button("記録を更新する", type="primary")
                    
                    if submitted:
                        save_record(
                            user_name, 
                            category, 
                            item["id"], 
                            item["title"], 
                            new_level, 
                            comment
                        )
                        
                        # 成功メッセージとエフェクト
                        if new_level >= 3 and current_level < 3:
                            st.balloons()
                            st.success(f"おめでとうございます！「{item['title']}」が自立レベルになりました！🎉")
                        else:
                            st.success("保存しました！")
                        
                        # データを反映させるためにリロード
                        st.rerun()

# --- フッター ---
st.divider()
st.caption("Powered by Hospital DX Team / Ver 2.0")
