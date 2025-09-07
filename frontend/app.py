import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from streamlit_autorefresh import st_autorefresh
from datetime import datetime
import numpy as np

# 设置页面配置
st.set_page_config(
    page_title="用户行为分析",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stTitle {
        font-family: 'Segoe UI', sans-serif;
        color: #1a1a1a;
        font-weight: 600;
    }
    .stSubheader {
        font-family: 'Segoe UI', sans-serif;
        color: #2c3e50;
        font-weight: 500;
    }
    .sidebar .sidebar-content {
        background-color: #ffffff;
    }
    div[data-testid="stDecoration"] {
        background-image: linear-gradient(90deg, #4CAF50, #2196F3);
    }
    </style>
    """, unsafe_allow_html=True)

# 每5秒自动刷新一次
st_autorefresh(interval=5000)

st.title("📊 实时用户行为分析")
st.markdown("#### 实时监控用户访问路径和页面停留时间")

# 从后端API获取数据
try:
    response = requests.get("http://127.0.0.1:8000/api/timeline")
    if response.status_code == 200:
        timelines = response.json()
        
        if not timelines:
            st.info("暂无用户访问数据。请等待数据收集...")
        else:
            # 1. 收集所有页面和时间范围
            all_pages = set()
            all_events = []
            min_time = None
            max_time = None
            
            for session in timelines:
                for event in session["events"]:
                    all_pages.add(event["screen_id"])
                    start_time = datetime.fromisoformat(event["timestamp"].replace('Z', '+00:00'))
                    duration = event["duration"]
                    end_time = pd.Timestamp(start_time) + pd.Timedelta(seconds=duration)
                    
                    all_events.append({
                        "session": session["session_id"],
                        "page": event["screen_id"],
                        "start": start_time,
                        "end": end_time,
                        "duration": duration
                    })
                    
                    if min_time is None or start_time < min_time:
                        min_time = start_time
                    if max_time is None or end_time > max_time:
                        max_time = end_time
            
            # 2. 为每个页面分配一个固定的y轴位置
            pages_list = sorted(list(all_pages))
            page_positions = {page: i for i, page in enumerate(pages_list)}

            # 3. 创建图形
            fig = go.Figure()
            
            # 定义现代化的配色方案
            COLORS = {
                'background': '#ffffff',
                'grid': '#f0f2f6',
                'reference': '#e9ecef',
                'event': '#3498db',  # 主要事件颜色
                'transition': '#34495e',  # 转换线颜色
                'hover': '#2ecc71'  # 悬停时的颜色
            }
            
            # 添加水平参考线（表示页面层级）
            for page, pos in page_positions.items():
                fig.add_shape(
                    type="rect",
                    x0=min_time,
                    x1=max_time,
                    y0=pos - 0.3,
                    y1=pos + 0.3,
                    fillcolor=COLORS['reference'],
                    opacity=0.1,
                    line_width=0,
                    layer="below"
                )
            
            # 添加页面停留时间（水平粗线）
            for event in all_events:
                fig.add_trace(go.Scatter(
                    x=[event["start"], event["end"]],
                    y=[page_positions[event["page"]], page_positions[event["page"]]],
                    mode="lines",
                    line=dict(
                        color=COLORS['event'],
                        width=12,
                        shape='spline',
                    ),
                    name=event["page"],
                    text=f"<b>{event['page']}</b><br>会话: {event['session']}<br>开始: {event['start'].strftime('%H:%M:%S')}<br>停留: {event['duration']}秒",
                    hoverinfo="text",
                    hoverlabel=dict(
                        bgcolor=COLORS['hover'],
                        font_size=13,
                        font_family="Segoe UI"
                    ),
                    showlegend=False
                ))
            
            # 添加页面间的转换（箭头连接线）
            for session in timelines:
                events = session["events"]
                for i in range(len(events) - 1):
                    current = events[i]
                    next_event = events[i + 1]
                    
                    # 计算箭头的起点和终点
                    start_time = datetime.fromisoformat(current["timestamp"].replace('Z', '+00:00'))
                    end_time = start_time + pd.Timedelta(seconds=current["duration"])
                    next_start = datetime.fromisoformat(next_event["timestamp"].replace('Z', '+00:00'))
                    
                    y0 = page_positions[current["screen_id"]]
                    y1 = page_positions[next_event["screen_id"]]
                    
                    # 添加平滑的转换线
                    x_bezier = [end_time, 
                              end_time + (next_start - end_time) * 0.5,
                              next_start]
                    y_bezier = [y0, (y0 + y1) / 2, y1]
                    
                    fig.add_trace(go.Scatter(
                        x=x_bezier,
                        y=y_bezier,
                        mode="lines",
                        line=dict(
                            color=COLORS['transition'],
                            width=2,
                            shape='spline'
                        ),
                        opacity=0.6,
                        showlegend=False
                    ))
            
            # 更新布局
            fig.update_layout(
                template="plotly_white",
                paper_bgcolor=COLORS['background'],
                plot_bgcolor=COLORS['background'],
                title=dict(
                    text="用户行为时序图",
                    x=0.5,
                    font=dict(
                        family="Segoe UI",
                        size=24,
                        color="#2c3e50"
                    )
                ),
                showlegend=True,
                hovermode='closest',
                margin=dict(b=20, l=100, r=20, t=60),
                height=600,
                xaxis=dict(
                    title=dict(
                        text="时间",
                        font=dict(family="Segoe UI", size=14)
                    ),
                    showgrid=True,
                    gridcolor=COLORS['grid'],
                    zeroline=False,
                    showline=True,
                    linewidth=1,
                    linecolor=COLORS['grid']
                ),
                yaxis=dict(
                    title=dict(
                        text="页面",
                        font=dict(family="Segoe UI", size=14)
                    ),
                    showgrid=False,
                    ticktext=pages_list,
                    tickvals=list(page_positions.values()),
                    tickfont=dict(family="Segoe UI", size=12),
                    zeroline=False,
                    showline=True,
                    linewidth=1,
                    linecolor=COLORS['grid']
                ),
                hoverlabel=dict(
                    font_size=13,
                    font_family="Segoe UI"
                ),
                transition=dict(
                    duration=500,
                    easing="cubic-in-out"
                )
            )

            # 显示图表
            st.plotly_chart(fig, use_container_width=True)

            # 创建三列布局用于显示关键指标
            col1, col2, col3 = st.columns(3)
            
            # 计算基本统计信息
            total_sessions = len(timelines)
            total_pages = len(all_pages)
            total_events = len(all_events)
            avg_duration = np.mean([event["duration"] for event in all_events])
            transitions = sum(len(session["events"]) - 1 for session in timelines)
            
            # 使用现代化的指标卡片显示
            with col1:
                st.markdown("""
                    <div style='padding: 20px; background: white; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                        <h3 style='margin:0; color: #2c3e50; font-size: 16px;'>活跃用户</h3>
                        <p style='font-size: 24px; margin: 10px 0; color: #3498db;'>{}</p>
                        <p style='margin:0; color: #7f8c8d; font-size: 12px;'>当前会话数</p>
                    </div>
                """.format(total_sessions), unsafe_allow_html=True)

            with col2:
                st.markdown("""
                    <div style='padding: 20px; background: white; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                        <h3 style='margin:0; color: #2c3e50; font-size: 16px;'>平均停留时间</h3>
                        <p style='font-size: 24px; margin: 10px 0; color: #2ecc71;'>{:.1f}秒</p>
                        <p style='margin:0; color: #7f8c8d; font-size: 12px;'>每页面平均</p>
                    </div>
                """.format(avg_duration), unsafe_allow_html=True)

            with col3:
                st.markdown("""
                    <div style='padding: 20px; background: white; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                        <h3 style='margin:0; color: #2c3e50; font-size: 16px;'>页面切换</h3>
                        <p style='font-size: 24px; margin: 10px 0; color: #e74c3c;'>{}</p>
                        <p style='margin:0; color: #7f8c8d; font-size: 12px;'>总转换次数</p>
                    </div>
                """.format(transitions), unsafe_allow_html=True)
            
            # 计算并显示每个页面的访问统计
            page_stats = {}
            for event in all_events:
                page = event["page"]
                if page not in page_stats:
                    page_stats[page] = {"visits": 0, "total_duration": 0}
                page_stats[page]["visits"] += 1
                page_stats[page]["total_duration"] += event["duration"]
            
            stats_df = pd.DataFrame([
                {
                    "页面": page,
                    "访问次数": stats["visits"],
                    "平均停留时间(秒)": round(stats["total_duration"] / stats["visits"], 1)
                }
                for page, stats in page_stats.items()
            ]).sort_values("访问次数", ascending=False)
            
            # 使用现代化的表格样式
            st.markdown("""
                <style>
                .dataframe {
                    font-family: 'Segoe UI', sans-serif;
                    border-collapse: collapse;
                    width: 100%;
                    background: white;
                    border-radius: 10px;
                    overflow: hidden;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                .dataframe th {
                    background-color: #f8f9fa;
                    padding: 12px;
                    text-align: left;
                    font-weight: 500;
                    color: #2c3e50;
                }
                .dataframe td {
                    padding: 12px;
                    border-top: 1px solid #f0f2f6;
                }
                </style>
            """, unsafe_allow_html=True)
            
            st.subheader("📈 页面访问详情")
            st.dataframe(
                stats_df,
                hide_index=True,
                column_config={
                    "页面": "页面名称",
                    "访问次数": st.column_config.NumberColumn(
                        "访问次数",
                        help="页面被访问的总次数",
                        format="%d"
                    ),
                    "平均停留时间(秒)": st.column_config.NumberColumn(
                        "平均停留时间",
                        help="用户在该页面的平均停留时间（秒）",
                        format="%.1f秒"
                    )
                }
            )
            
except requests.exceptions.ConnectionError:
    st.error("无法连接到后端服务。请确保后端服务正在运行 (http://127.0.0.1:8000)")
except Exception as e:
    st.error(f"发生错误: {str(e)}")
