import streamlit as st
import pandas as pd
import altair as alt
from io import BytesIO
from pathlib import Path

st.set_page_config(page_title="里程數查詢系統", layout="wide")

@st.cache_data
def load_excel(file: BytesIO | str):
    """讀取 Excel，回傳所有工作表的 DataFrame 字典"""
    return pd.read_excel(file, sheet_name=None)


def main():
    st.title("🚚 kmapp 里程數查詢系統")
    st.markdown("上傳新版 **kmapp里程數.xlsx** 或使用預設範例。")

    # ---------- 1. 載入資料 ----------
    uploaded = st.file_uploader("選擇 Excel 檔 (*.xlsx)", type=["xlsx"])
    if uploaded:
        sheets = load_excel(uploaded)
    else:
        default_path = Path(__file__).parent / "kmapp里程數.xlsx"
        if default_path.exists():
            sheets = load_excel(default_path)
            st.info("使用範例資料：kmapp里程數.xlsx")
        else:
            st.error("找不到預設範例，請先上傳檔案。")
            st.stop()

    # ---------- 2. 路線選擇 ----------
    routes = list(sheets.keys())
    route = st.sidebar.selectbox("選擇路線", routes)
    df = sheets[route]

    # ---------- 3. 關鍵字篩選 ----------
    keyword = st.text_input("地名關鍵字篩選", "")
    if keyword:
        df_display = df[df["地名"].str.contains(keyword, na=False)]
    else:
        df_display = df

    st.subheader(f"📍 {route} 路線資料")
    st.dataframe(df_display, use_container_width=True)

    # ---------- 4. 摘要指標 ----------
    col1, col2 = st.columns(2)
    with col1:
        st.metric("資料筆數", len(df_display))
    with col2:
        if "里程定位" in df_display.columns:
            st.metric("最大里程定位 (km)", df_display["里程定位"].max())

    # ---------- 5. 圖表 ----------
    if {"里程定位", "運輸距離"}.issubset(df_display.columns):
        st.subheader("里程定位 vs. 運輸距離")
        chart = (
            alt.Chart(df_display)
            .mark_line(point=True)
            .encode(
                x="里程定位",
                y="運輸距離",
                tooltip=["地名", "里程定位", "運輸距離"],
            )
            .properties(height=400)
        )
        st.altair_chart(chart, use_container_width=True)

    # ---------- 6. 下載功能 ----------
    csv = df_display.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="下載篩選結果 (CSV)",
        data=csv,
        file_name=f"{route}_mileage_filtered.csv",
        mime="text/csv",
    )


if __name__ == "__main__":
    main()
