import pandas as pd
import streamlit as st
import time
import plotly.graph_objs as go
import altair as alt
from utils import Utils
import numpy as np
import plotly.express as px
import altair as alt

# Graphical Functions
def plot_gauge(cpu_value, title):
    cpu_percentage = cpu_value * 100
    if cpu_percentage < 80:
        color = "green"
    elif 80 <= cpu_percentage < 90:
        color = "orange"
    else:
        color = "red"
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=cpu_percentage,
        domain={'x': [0, 1], 'y': [0, 1]},
        number={
            'suffix': "%",
            'font': {'size': 24, 'color': color, 'family': 'Inter', 'weight': 100},
        },
        gauge={
            'axis': {'range': [0, 100], 'visible': False},
            'bar': {'color': color},  
            'bgcolor': "rgba(234, 234, 234, 0.1)",
            'borderwidth': 0,
            'shape': "angular",
            'threshold': {
                'line': {'color': "white", 'width': 4},
                'thickness': 0.55,
                'value': cpu_percentage
            }
        },
        title={
            'text': f"<b>{title}</b>",
            'font': {'size': 16, 'family': 'Inter', 'weight': 'normal'},
            'align': 'center'
        }
    ))
    fig.update_layout(
        height=220,
        margin=dict(l=10, r=10, t=20, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        font={'color': "white", 'family': "Inter"}
    )
    return fig

def plot_scatter(df, xlim, ylim):
    source = df.copy()
    chart = alt.Chart(source).mark_circle(size=100).encode(

        x = alt.X('downlink', scale=alt.Scale(domain=[0, xlim])),
        y = alt.Y('uplink', scale=alt.Scale(domain=[0, ylim])),
        color=alt.Color('category', scale=alt.Scale(domain=['safe','moderate risk','dangerous'], range=['green','yellow','red'])) 
    ).interactive()
    st.altair_chart(chart, use_container_width=True)

def plot_risk_level(data, rol):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['Risk'],
        mode='lines',
        line=dict(color='orange'),
        name='Immediate Risk'
    ))

    fig.add_trace(go.Scatter(
        x=data.index,
        y=rol,
        mode='lines',
        line=dict(color='cyan'),
        name='Rolling Mean Risk'
    ))

    fig.update_layout(
        xaxis_title='',
        yaxis_title='%',
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={'color': "white", 'family': "Inter"},
        margin=dict(l=10, r=10, t=10, b=10),
        height=400
    )
    return fig

# Styling Functions
def link_risk_icon(risk_analysis_result):
    if risk_analysis_result == "Mean Risk drop or steady risk":
        return "https://i.imgur.com/17lYTAp.png"
    elif risk_analysis_result == "Significant Mean Risk increase":
        return "https://i.imgur.com/sWC2ygJ.png"

def font_style():
    return(
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');

        .title {
            font-family: 'Inter', sans-serif;
            font-weight: 700;
            font-size: 24px;
        }
        .subtitle {
            font-family: 'Inter', sans-serif;
            font-weight: 300;
            font-size: 15px;
            }
        .status_text {
            font-family: 'Inter', sans-serif;
            font-weight: 500;
            font-size: 20px;
                }
        .progress_text {
            font-family: 'Inter', sans-serif;
            font-weight: 300;
            font-size: 13px;
                }
        </style>
        """, unsafe_allow_html=True))

def add_vertical_space(lines: int = 1):
    for _ in range(lines):
        st.write("")

def main():
    # General Configuration and Styling
    st.set_page_config(page_title="Failure Predictor", page_icon=":material/search_insights:", layout="wide", initial_sidebar_state="auto")
    app = Utils()
    font_style()

    st.title(":material/search_insights: FAILURE PREDICTOR", anchor=False)
    add_vertical_space(1)

    # About Section
    c1, c2 = st.columns([0.6, 0.4])
    with c1:
        with st.expander("About"):
            st.markdown("""     
                This app is a real-time failure predictor, collecting data from a network server and predicting the likelihood of a failure.
                Also provides a risk assessment based on the predicted likelihood of a failure and displays the status of the prediction, the
                CPU usage, the risk level, and the risk assessment.
            """)
            st.image("https://i.imgur.com/dghLTqg.png", use_column_width=False, width=600) 
    add_vertical_space(1)

    # Progress, Status and CPU Usage Section
    risk_analysis_result = "Awaiting Prediction"
    c3, c4 = st.columns([0.4, 0.6], gap="large")
    with c3:
        st.markdown(f'<p class="title">Progress</p>', unsafe_allow_html=True)
        progress_cols = st.columns([0.15, 0.85])
        with progress_cols[0]:
            status_text = st.empty()
        with progress_cols[1]:
            progress_bar = st.empty() 
        st.button("RUN", type='secondary', help="Run the Failure Predictor")
        st.markdown(f'<p class="title">Status</p>', unsafe_allow_html=True)
        status_cols = st.columns([0.1, 0.9], vertical_alignment="center")
        with status_cols[0]:
            icon = st.empty()
        with status_cols[1]:
            status_display = st.empty() 
            status_display.markdown(f'<p class="status_text">{risk_analysis_result}</p>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<p class="title">CPU Usage</p>', unsafe_allow_html=True)
        gauge_cols = st.columns(4)
        gauge_plots = [col.empty() for col in gauge_cols] 

    # Risk Level and Risk Assessment Section
    c5, c6 = st.columns([0.4, 0.6], gap="large") 
    with c5:
        st.markdown(f'<p class="title">Risk Level</p>', unsafe_allow_html=True)
        last_rows = pd.DataFrame(columns=['Risk'])
        chart = st.line_chart(last_rows)

    with c6:
        st.markdown(f'<p class="title">Risk Assessment</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="subtitle">DOWNLINK X UPLINK</p>', unsafe_allow_html=True)
        chart_3 = st.empty()

    # Main Loop for Updating Data
    for i in range(0, 100, 2): 
        sample = app.get_sample()
        pred = app.make_pred(sample)
        pred_percentage = pred * 100  
        pred_percentage = float(pred_percentage)  
        risk_analysis_result = app.risk_analysis(pred)
        status_display.markdown(f'<p class="status_text">{risk_analysis_result}</p>', unsafe_allow_html=True)
        icon.image(link_risk_icon(risk_analysis_result))

        # Risk Level Update
        new_row = pd.DataFrame({'Risk': [pred_percentage]})
        last_rows = pd.concat([last_rows, new_row]).reset_index(drop=True)
        rolling = app.get_roll_mean()
        risk_fig = plot_risk_level(last_rows, rolling)
        chart.plotly_chart(risk_fig)

        cpu_values = sample[['cpu_1', 'cpu_2', 'cpu_3', 'cpu_4']].values[0]
        for idx, cpu_val in enumerate(cpu_values):
            gauge_plots[idx].plotly_chart(plot_gauge(cpu_val, f'CPU {idx+1}'), use_container_width=True)

        with chart_3:
            app.update_data(sample, pred)
            plot_scatter(app.get_data(), 100000, 60000)

        status_text.markdown(f'<p class="progress_text">{i}% complete</p>', unsafe_allow_html=True)
        progress_bar.progress(i) 
        time.sleep(1)

if __name__ == "__main__":
    main()
