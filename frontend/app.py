import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.title("📊 用户路径可视化 (PoC Demo)")

uploaded_file = st.file_uploader("上传 CSV 文件", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.write("数据预览：", df.head())

    # 假设 CSV 格式: session_id, screen_id, timestamp
    if {"session_id", "screen_id"}.issubset(df.columns):
        # 构造路径（简单版：相邻 screen_id 构成边）
        edges = []
        for sid, group in df.groupby("session_id"):
            screens = group["screen_id"].tolist()
            for i in range(len(screens)-1):
                edges.append((screens[i], screens[i+1]))

        edge_df = pd.DataFrame(edges, columns=["source", "target"])
        edge_counts = edge_df.value_counts().reset_index(name="count")

        # Sankey 图
        labels = list(set(edge_counts["source"]) | set(edge_counts["target"]))
        label_index = {label: i for i, label in enumerate(labels)}

        fig = go.Figure(data=[go.Sankey(
            node=dict(label=labels, pad=20, thickness=20),
            link=dict(
                source=edge_counts["source"].map(label_index),
                target=edge_counts["target"].map(label_index),
                value=edge_counts["count"]
            )
        )])
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("CSV 必须包含列: session_id, screen_id")
