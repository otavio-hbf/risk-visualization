import pandas as pd
import streamlit as st
import time
import matplotlib.pyplot as plt
from utils import Utils
import numpy as np
import plotly.graph_objs as go
import plotly.express as px
import altair as alt

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

def color(risk):
    if risk > 0.6:
        return "red"
    elif risk < 0.3:
        return "green"
    else:
        return "yellow"

def link_risk_icon(risk_analysis_result):
    if risk_analysis_result == "Mean Risk drop or steady risk":
        return "https://i.imgur.com/17lYTAp.png"
    elif risk_analysis_result == "Significant Mean Risk increase":
        return "https://i.imgur.com/sWC2ygJ.png"
    
def main():
    st.set_page_config(page_title="Failure Predictor", page_icon=":material/search_insights:", layout="centered", initial_sidebar_state="auto")
    
    st.title(":material/search_insights: FAILURE PREDICTOR")
    
    app = Utils()
    
    risk_analysis_result = "Awaiting Prediction"
    
    with st.container():
        c3, c4 = st.columns([2, 1])
        with c3:
            st.markdown("### STATUS")
            status_cols = st.columns([0.1, 0.9])
            with status_cols[0]:
                icon = st.empty()
            with status_cols[1]:
                status_display = st.empty() 
                status_display.write(f"{risk_analysis_result}")
        with c4:
            st.markdown("### PROGRESS")
            progress_cols = st.columns([0.15, 0.85])
            with progress_cols[0]:
                status_text = st.empty()
            with progress_cols[1]:
                progress_bar = st.empty() 
            st.button("RUN", type='secondary', help="Run the Failure Predictor")
        
        c1, c2 = st.columns([2, 1]) 
        with c1:
            st.markdown("### RISK LEVEL")
            last_rows = []
            chart = st.line_chart(last_rows)

        with c2:
            st.markdown("### CPU USAGE")
            gauge_cols = st.columns(2)
            gauge_plots = [col.empty() for col in gauge_cols] 

            gauge_cols2 = st.columns(2) 
            gauge_plots.extend([col.empty() for col in gauge_cols2]) 

        st.markdown("### RISK ASSESSMENT\nDownlink x Uplink")
        chart_data3 = pd.DataFrame()
        chart_3 = st.empty()
        st.image("https://i.imgur.com/dghLTqg.png")

        
        for i in range(1, 100, 2): 
                sample = app.get_sample()
                pred = [app.make_pred(sample)]
                risk_analysis_result = app.risk_analysis(pred)
                status_display.write(f"{risk_analysis_result}")  
                icon.image(link_risk_icon(risk_analysis_result))

                with c1:
                    chart.add_rows(pred)

                cpu_values = sample[['cpu_1', 'cpu_2', 'cpu_3', 'cpu_4']].values[0]
                for idx, cpu_val in enumerate(cpu_values):
                    gauge_plots[idx].plotly_chart(plot_gauge(cpu_val, f'CPU {idx+1}'), use_container_width=True)

                with chart_3:
                    app.update_data(sample, pred[0])
                    plot_scatter(app.get_data(), 100000, 60000)
                status_text.text("%i%%" % i)
                progress_bar.progress(i)  

                time.sleep(1)
 



if __name__ == "__main__":
    main()

