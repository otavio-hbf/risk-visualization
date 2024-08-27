import pandas as pd
import streamlit as st
import time
import matplotlib.pyplot as plt
from utils import Utils
import numpy as np


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