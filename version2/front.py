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
            'font': {'size': 24, 'color': color}
        },
        gauge={
            'axis': {'range': [0, 100], 'visible': False},
            'bar': {'color': color},
            'bgcolor': "rgba(0,0,0,0)",
            'borderwidth': 0,
            'shape': "angular",
            'threshold': {
                'line': {'color': "white", 'width': 4},
                'thickness': 0.75,
                'value': cpu_percentage
            }
        },
        title={
            'text': f"<b>{title}</b>",
            'font': {'size': 16},
            'align': 'center'
        }
    ))
    fig.update_layout(
        height=150,
        margin=dict(l=10, r=10, t=30, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        font={'color': "white", 'family': "Arial"}
    )
    
    return fig


def plot_scatter(df, xlim, ylim):
    source = df.copy()
    
    chart = alt.Chart(source).mark_circle().encode(

        x = alt.X('downlink', scale=alt.Scale(domain=[0, xlim])),
        y = alt.Y('uplink', scale=alt.Scale(domain=[0, ylim])),
        color=alt.Color('category', scale=alt.Scale(domain=['safe','moderate risk','dangerous'], range=['green','yellow','red'])) 
    ).interactive()

    st.altair_chart(chart, use_container_width=True)

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
            font-size: 36px;
        }
        .section_title {
            font-family: 'Inter', sans-serif;
            font-weight: 300;
            font-size: 20px;
                }
        .status_text {
            font-family: 'Inter', sans-serif;
            font-weight: 500;
            font-size: 20px;
                }
        .progress_text {
            font-family: 'Inter', sans-serif;
            font-weight: 300;
            font-size: 14px;
                }
        </style>
        """, unsafe_allow_html=True))

def add_vertical_space(lines: int = 1):
    for _ in range(lines):
        st.write("")

def main():

    #General Configuration and Styling
    st.set_page_config(page_title="Failure Predictor", page_icon=":material/search_insights:", layout="wide", initial_sidebar_state="auto")
    app = Utils()
    font_style()

    st.title(":material/search_insights: FAILURE PREDICTOR", anchor=False)
    add_vertical_space(1)

    #About Section
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

    #Progress Section
    c3, c4 = st.columns([0.6, 0.4])
    with c3: 
        st.markdown("### Progress")
        progress_cols = st.columns([0.15, 0.85])
        with progress_cols[0]:
            status_text = st.empty()
        with progress_cols[1]:
            progress_bar = st.empty() 
        st.button("RUN", type='secondary', help="Run the Failure Predictor")

    #Status and CPU Usage Section
    risk_analysis_result = "Awaiting Prediction"
    c5, c6 = st.columns([0.4, 0.6])
    with c5:
        st.markdown("### Status")
        status_cols = st.columns([0.1, 0.9], vertical_alignment="center")
        with status_cols[0]:
            icon = st.empty()
        with status_cols[1]:
            status_display = st.empty() 
            status_display.markdown(f'<p class="status_text">{risk_analysis_result}</p>', unsafe_allow_html=True)
    with c6:
        st.markdown("### CPU Usage")
        gauge_cols = st.columns(4)
        gauge_plots = [col.empty() for col in gauge_cols] 


    add_vertical_space(1)
    
    #Risk Assessment Section and Risk Level
    c7, c8 = st.columns([0.5, 0.5], gap="large") 
    with c7:
        st.markdown("### RISK ASSESSMENT\nDOWNLINK X UPLINK")
        chart_3 = st.empty()

    with c8:
        st.markdown("### RISK LEVEL")
        last_rows = []
        chart = st.line_chart(last_rows)

    #Main Loop
    for i in range(1, 100, 2): 
        sample = app.get_sample()
        pred = [app.make_pred(sample)]
        risk_analysis_result = app.risk_analysis(pred)
        status_display.markdown(f'<p class="status_text">{risk_analysis_result}</p>', unsafe_allow_html=True)
        icon.image(link_risk_icon(risk_analysis_result))

        with c1:
            chart.add_rows(pred)

        cpu_values = sample[['cpu_1', 'cpu_2', 'cpu_3', 'cpu_4']].values[0]
        for idx, cpu_val in enumerate(cpu_values):
            gauge_plots[idx].plotly_chart(plot_gauge(cpu_val, f'CPU {idx+1}'), use_container_width=True)

        with chart_3:
            app.update_data(sample, pred[0])
            plot_scatter(app.get_data(), 100000, 60000)

        status_text.markdown(f'<p class="progress_text">{i}% complete</p>', unsafe_allow_html=True)
        progress_bar.progress(i)  
        #progress_bar.progress(i, f'{i}% complete')  

        time.sleep(1)

if __name__ == "__main__":
    main()