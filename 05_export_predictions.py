# -*- coding: utf-8 -*-
"""
Created on Thu Nov 16 15:09:00 2021

@author: Luis Guevara
"""

#----------------------------------------------------------------------------

from flask import Flask, render_template
import pickle
import configparser
from datetime import datetime
from datetime import timedelta
app = Flask(__name__, static_url_path='/static')

config = configparser.ConfigParser()
config.read('config.ini')
CODE_COUNTRY = config['DEFAULT']['CODE_COUNTRY']

#------------------------------------ FLASK -----------------------------------


with open(f'predictions/pl_predictions_{CODE_COUNTRY}.csv', 'rb') as myFile:
    pl_pred = pickle.load(myFile)

with open(f'clean_fixtures_and_dataframes/{CODE_COUNTRY}/2019_2020_2021_{CODE_COUNTRY}_additional_stats_dict.txt', 'rb') as myFile:
    additional_stats_dict = pickle.load(myFile)

#removing all past predictions if they still exist in the predictions df
current_date = datetime.today().strftime('%Y-%m-%d')
final_date = datetime.now() + timedelta(days=10)
print(current_date)
print(final_date)
for j in range(len(pl_pred)):
    game_date = pl_pred['Game Date'].loc[j]
    if game_date < current_date:
        pl_pred = pl_pred.drop([j], axis=0)
pl_pred = pl_pred.reset_index(drop=True)

print(pl_pred)
