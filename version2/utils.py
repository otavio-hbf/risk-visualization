import pandas as pd
import numpy as np
from joblib import load
from random import randint
import requests
import json

class Utils:

    def __init__(self):
        self.model = load("models/xgb_cpu.joblib")
        self.data = pd.DataFrame()
        self.max_size = len(self.data)
        self.risk_arr = []
        self.sum_dl_list = []
        self.sum_ul_list = []
        self.risk_list = []
        self.category_list = []
        self.mcs_data = []

    def update_list(self,name, data):
        if(name == "dl"): self.sum_dl_list.append(data)
        elif(name =="ul"): self.sum_ul_list.append(data)
        elif(name =="risk"): self.risk_list.append(data)
        elif(name =="category"): self.category_list.append(data)
        elif(name == "mcs"): self.mcs_data.append(data)
        else: print(f"impossible to update {name} list")


    def update_data(self, sample, prediction):
        self.update_list("dl", self.get_sum(sample, dl=True)[0])
        self.update_list("ul", self.get_sum(sample, dl=False)[0])
        self.update_list("risk", prediction)
        self.update_list("category", self.category(prediction))

        new_data = pd.DataFrame({"downlink" : self.sum_dl_list, "uplink": self.sum_ul_list, "risk":self.risk_list, "category":self.category_list})
        self.data = new_data

    def make_pred(self,sample):
        
        preds = self.model.predict_proba(sample)
        return preds[0][1]

    def get_sample(self):
        
        sample_json = requests.get("http://localhost:5000/random")
        json_string = sample_json.text
        json_dict = json.loads(json_string)

        sample = pd.DataFrame.from_dict(json_dict, orient='index').T

        sample = sample[['mcs_dl_1', 'mcs_ul_1', 'dl_kbps_1', 'ul_kbps_1', 'mcs_dl_2',
                        'mcs_ul_2', 'dl_kbps_2', 'ul_kbps_2', 'mcs_dl_3', 'mcs_ul_3',
                        'dl_kbps_3', 'ul_kbps_3', 'mcs_dl_4', 'mcs_ul_4', 'dl_kbps_4',
                        'ul_kbps_4', 'cpu_1', 'cpu_2', 'cpu_3', 'cpu_4']]

        return sample

    def update_risk(self, risk):

        if(len(self.risk_arr) < 5):
            self.risk_arr.append(risk)
        else:
            self.risk_arr.pop(0)
            self.risk_arr.append(risk)
        
    def risk_analysis(self, risk):
        prior_risk = np.mean(self.risk_arr)
        self.update_risk(risk)
        current_risk = np.mean(self.risk_arr)

        risk_diff = current_risk - prior_risk

        if(risk_diff > 0.1*prior_risk):
            return "Significant Mean Risk increase"
        else:
            return "Mean Risk drop or steady risk"

    def get_sum(self, sample, dl):

        if(dl):
            sum = sample[['dl_kbps_1', 'dl_kbps_2', 'dl_kbps_3', 'dl_kbps_4']].apply(lambda x: np.sum([x.dl_kbps_1,x.dl_kbps_2,x.dl_kbps_3,x.dl_kbps_4]), axis=1)
        else:
            sum = sample[['ul_kbps_1', 'ul_kbps_2', 'ul_kbps_3', 'ul_kbps_4']].apply(lambda x: np.sum([x.ul_kbps_1,x.ul_kbps_2,x.ul_kbps_3,x.ul_kbps_4]), axis=1)

        return sum.values
    
    def get_data(self):
        
        return self.data
    
    def category(self, risk):
        if(risk > 0.6):
            return "dangerous"
        elif(risk < 0.3):
            return "safe"
        else:
            return "moderate risk"
