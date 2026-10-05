import streamlit as st
import pandas as pd
import numpy as np
import time
import os
from datetime import datetime, timedelta

st.set_page_config(
    page_title="居家银龄智护｜仿真演示系统",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "sim_running" not in st.session_state:
    st.session_state.sim_running = False

if "heart_rate" not in st.session_state:
    st.session_state.heart_rate = 72
if "spo2" not in st.session_state:
    st.session_state.spo2 = 97
if "sleep_score" not in st.session_state:
    st.session_state.sleep_score = 78
if "activity_step" not in st.session_state:
    st.session_state.activity_step = 3200

if "robot_status" not in st.session_state:
    st.session_state.robot_status = "待机"
if "robot_battery" not in st.session_state:
    st.session_state.robot_battery = 86

if "alarm_list" not in st.session_state:
    st.session_state.alarm_list = []

if "history_data" not in st.session_state:
    st.session_state.history_data = []


def gen_health_data(is_fall: bool = False):
    hr = int(np.random.normal(loc=73, scale=6))
    spo2 = int(np.random.normal(loc=96, scale=2))
    sleep = int(np.random.normal(loc=76, scale=7))
    step = int(np.random.normal(loc=3000, scale=800))
    if is_fall:
        hr = 126
        spo2 = 88
        step = 0
    return {
        "time": datetime.now(),
        "heart_rate": max(45, min(140, hr)),
        "spo2": max(80, min(100, spo2)),
        "sleep_score": max(40, min(100, sleep)),
        "activity_step": max(0, step)
    }


def add_alarm(level: str, title: str, content: str):
    new_alarm = {
        "alarm_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "level": level,
        "title": title,
        "content": content
    }
    st.session_state.alarm_list.insert(0, new_alarm)


with st.sidebar:
    st.header("🎛️ 仿真控制面板")
    st.divider()
    st.session_state.sim_running = st.checkbox("开启健康数据模拟", value=st.session_state.sim_running)
    st.subheader("🧪 事件模拟触发")
    btn_fall = st.button("🔴 模拟老人发生跌倒事件（黄金响应链）")
    btn_abnormal_hr = st.button("🟠 模拟心率异常升高")
    btn_clear_alarm = st.button("🗑️ 清空全部告警记录")
    st.divider()
    st.markdown("""
> **仿真说明**
> 1. 本系统为【居家银龄智护】原型演示，无真实硬件
> 2. 模拟链路：手环采集 → 机器人边缘复核 → 云端告警 → 子女端展示
> 3. 四层架构：感知层‑边缘层‑平台层‑应用层
""")

if btn_fall:
    fall_data = gen_health_data(is_fall=True)
    st.session_state.heart_rate = fall_data["heart_rate"]
    st.session_state.spo2 = fall_data["spo2"]
    st.session_state.activity_step = fall_data["activity_step"]
    st.session_state.robot_status = "抵近复核"
    add_alarm("紧急", "⚠️ 跌倒告警触发", "手环检测跌倒，机器人正在移动至老人位置进行语音复核，30s内推送子女紧急联系人")
    st.warning("✅ 跌倒事件模拟已触发：启动黄金响应链！")
    time.sleep(1)
    st.session_state.robot_status = "待机"

if btn_abnormal_hr:
    st.session_state.heart_rate = 118
    add_alarm("关注", "心率异常", f"监测到静息心率 {st.session_state.heart_rate} 次/分，偏离个人基线，请留意老人状态。")
    st.info("✅ 心率异常模拟触发")

if btn_clear_alarm:
    st.session_state.alarm_list.clear()
    st.success("告警列表已清空")

if st.session_state.sim_running:
    new_point = gen_health_data()
    st.session_state.heart_rate = new_point["heart_rate"]
    st.session_state.spo2 = new_point["spo2"]
    st.session_state.sleep_score = new_point["sleep_score"]
    st.session_state.activity_step = new_point["activity_step"]
    st.session_state.history_data.append(new_point)
    if len(st.session_state.history_data) > 120:
        st.session_state.history_data = st.session_state.history_data[-120:]

st.title("🏠 居家银龄智护 —— 系统仿真演示平台")
st.markdown("模拟：智能手环（感知层） + AI实体机器人（边缘层） + 云平台 + 子女守护端，第七届国际青年人工智能大赛创意组项目原型")
st.divider()

col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    st.subheader("⌚感知层｜智能手环（贴身健康哨兵）")
    st.divider()
    st.metric(label="实时心率(次/分)", value=st.session_state.heart_rate)
    st.metric(label="血氧SpO2(%)", value=st.session_state.spo2)
    st.metric(label="昨日睡眠评分", value=st.session_state.sleep_score)
    st.metric(label="今日活动步数", value=st.session_state.activity_step)
    st.markdown("""
> 手环仿真：
> - 心率/血氧/睡眠/活动量采集
> - IMU跌倒检测、SOS一键呼救
> - BLE蓝牙向上把数据发送给AI机器人
""")

with col2:
    st.subheader("🤖边缘层｜AI实体陪伴机器人")
    st.divider()
    st.metric(label="机器人当前工作状态", value=st.session_state.robot_status)
    st.metric(label="机器人电池电量%", value=st.session_state.robot_battery)
    st.markdown("""
> 机器人边缘计算仿真：
> - 全屋自主巡航、主动寻人陪伴
> - 跌倒事件本地复核（TFLite轻量模型）
> - 大模型情感对话、用药作息提醒
> - **断网可本地运行，原始数据本地优先处理**
""")

with col3:
    st.subheader("👨‍👩‍👧应用层｜子女远程守护面板")
    st.divider()
    st.markdown("### 🚨 实时告警消息")
    if len(st.session_state.alarm_list) == 0:
        st.success("暂无告警，老人状态平稳 ✅")
    else:
        for alm in st.session_state.alarm_list[:6]:
            lvl = alm["level"]
            txt = f"**[{alm['alarm_time']}]【{lvl}】{alm['title']}**\n{alm['content']}"
            if lvl == "紧急":
                st.error(txt)
            elif lvl == "关注":
                st.warning(txt)
            else:
                st.info(txt)

st.divider()
st.subheader("☁️平台层｜云端时序数据 & 健康趋势")
if len(st.session_state.history_data) > 3:
    df_hist = pd.DataFrame(st.session_state.history_data)
    df_hist.set_index("time", inplace=True)
    st.line_chart(df_hist[["heart_rate", "spo2"]], height=260)
else:
    st.info("💡勾选左侧【开启健康数据模拟】，自动生成时序数据绘制趋势曲线")

st.divider()
st.subheader("📄模拟子女端：老人健康周报片段")
avg_hr = np.mean([d["heart_rate"] for d in st.session_state.history_data]) if st.session_state.history_data else 72
avg_step = np.mean([d["activity_step"] for d in st.session_state.history_data]) if st.session_state.history_data else 3000
st.markdown(f"""
> **居家银龄智护｜老人健康周报（仿真）**
> 统计周期：最近7天
> - 平均心率：{avg_hr:.1f} 次/分
> - 日均活动步数：{avg_step:.0f} 步
>
> 💡健康建议：
> 1. 若步数持续偏低，建议多进行室内慢走活动；
> 2. 心率持续高于基线，请及时带老人前往医疗机构检查；
> 3. 系统为辅助监测工具，**不替代临床医疗诊断**。
""")

st.divider()
st.caption("原型仿真演示｜第八届国际青年人工智能大赛，仅用于学习演示，不可用于真实医疗监护。")
