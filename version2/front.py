import pandas as pd
import streamlit as st
import time
import matplotlib.pyplot as plt
from utils import Utils
import numpy as np
import plotly.graph_objs as go
from plotly.subplots import make_subplots

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


def plot_scatter(x, y, risk, c_list, xlim, ylim):

    fig = plt.figure(figsize=(10, 6))
    plt.scatter(x, y, s=100, color=c_list , label='Data Points')
    plt.xlabel('Downlink')
    plt.ylabel('Uplink')
    plt.title('Downlink x Uplink : Risk Assesment')
    plt.xlim(xlim)
    plt.ylim(ylim)
    plt.legend()


    st.pyplot(fig)

def color(risk):
    if(risk > 0.6):
        return "red"
    elif(risk < 0.3):
        return "green"
    else:
        return "yellow"


def main():
    st.set_page_config(page_title="Failure Predictor", page_icon=":material/search_insights:", layout="centered", initial_sidebar_state="auto", menu_items=None)
    st.header("Failure Predictor")
    c1, c2= st.columns(2)
    app = Utils()

    progress_bar = st.sidebar.progress(0)
    status_text = st.sidebar.empty()
    risk_text = st.sidebar.empty()
    

    with st.container():
        c1.write("Risk Level")
        c2.write("MCS")

        with c1:
            last_rows = []
            chart = st.line_chart(last_rows)
        with c2:
            st.write("")
        
        with st.container():
            st.markdown("CPU Usage")
            gauge_cols = st.columns(4)  
            gauge_plots = [col.empty() for col in gauge_cols]  

        chart_data3 = pd.DataFrame()
        chart_3 = st.scatter_chart(chart_data3)

        for i in range(1, 100, 2):

            sample = app.get_sample()


            pred = [app.make_pred(sample)]
            risk_text.text(app.risk_analysis(pred))

            with c1:
                status_text.text("%i%% Complete" % i)
                chart.add_rows(pred)
                progress_bar.progress(i)
                        
            cpu_values = sample[['cpu_1', 'cpu_2', 'cpu_3', 'cpu_4']].values[0]
            for idx, cpu_val in enumerate(cpu_values):
                gauge_plots[idx].plotly_chart(plot_gauge(cpu_val, f'CPU {idx+1}'), use_container_width=True)


            with chart_3:
                app.update_list("dl", app.get_sum(sample, dl=True))
                app.update_list("ul", app.get_sum(sample, dl=False))
                app.update_list("risk", pred[0])
                app.update_list("color", color(pred[0]))

                data3 = pd.DataFrame({"downlink" : app.sum_dl_list, "uplink": app.sum_ul_list, "risk":app.risk_list, "color":app.color_list})

                plot_scatter(data3['downlink'].values, data3['uplink'].values, data3['risk'].values, data3['color'].values, (0, 60000), (0,100000))

            time.sleep(1)

        progress_bar.empty()
    st.button("run")

if __name__ == "__main__":
    main()