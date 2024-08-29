import pandas as pd
import streamlit as st
import time
import matplotlib.pyplot as plt
from utils import Utils
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import altair as alt

def plot_scatter(df, xlim, ylim):
    source = df.copy()
    
    chart = alt.Chart(source).mark_circle().encode(

        x = alt.X('downlink', scale=alt.Scale(domain=[0, xlim])),
        y = alt.Y('uplink', scale=alt.Scale(domain=[0, ylim])),
        color=alt.Color('category', scale=alt.Scale(domain=['safe','moderate risk','dangerous'], range=['green','yellow','red'])) 
    ).interactive()

    st.altair_chart(chart, use_container_width=True)


def main():
    c1, c2= st.columns(2)
    app = Utils()

    progress_bar = st.sidebar.progress(0)
    status_text = st.sidebar.empty()
    risk_text = st.sidebar.empty()
    

    with st.container():
        c1.write("Risk Level")
        c2.write("Cpu Usage")

        with c1:
            last_rows = []
            chart = st.line_chart(last_rows)
        with c2:
            chart_data = pd.DataFrame()
            chart_2 = st.bar_chart(chart_data)


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
                        
            with chart_2.container():
                chart_2_data = sample[['cpu_1', 'cpu_2', 'cpu_3', 'cpu_4']]
                data2 = pd.DataFrame({"name" : ['cpu_1', 'cpu_2', 'cpu_3', 'cpu_4'], "cpu": chart_2_data.values[0]})
                st.bar_chart(data2, x='name',y='cpu')


            with chart_3:
                app.update_data(sample, pred[0])
                plot_scatter(app.get_data(), 100000, 60000)

            time.sleep(1)

        progress_bar.empty()
    st.button("run")

if __name__ == "__main__":
    main()