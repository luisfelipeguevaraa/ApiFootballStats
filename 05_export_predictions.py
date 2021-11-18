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
import pandas as pd
app = Flask(__name__, static_url_path='/static')

config = configparser.ConfigParser()
config.read('config.ini')
CODE_COUNTRY = config['DEFAULT']['CODE_COUNTRY']

#------------------------------------ FLASK -----------------------------------


with open(f'predictions/pl_predictions_es.csv', 'rb') as myFile:
    pl_pred_es = pickle.load(myFile)
pl_pred_es.insert(len(pl_pred_es.columns), 'league', 'es')


with open(f'predictions/pl_predictions_it.csv', 'rb') as myFile:
    pl_pred_it = pickle.load(myFile)
pl_pred_it.insert(len(pl_pred_it.columns), 'league', 'it')


with open(f'predictions/pl_predictions_de.csv', 'rb') as myFile:
    pl_pred_de = pickle.load(myFile)
pl_pred_de.insert(len(pl_pred_de.columns), 'league', 'de')


with open(f'predictions/pl_predictions_fr.csv', 'rb') as myFile:
    pl_pred_fr = pickle.load(myFile)
pl_pred_fr.insert(len(pl_pred_fr.columns), 'league', 'fr')

pl_pred = pd.concat([pl_pred_es, pl_pred_it, pl_pred_de, pl_pred_fr ])
pl_pred = pl_pred.reset_index(drop=True)

with open(f'clean_fixtures_and_dataframes/{CODE_COUNTRY}/2019_2020_2021_{CODE_COUNTRY}_additional_stats_dict.txt', 'rb') as myFile:
    additional_stats_dict = pickle.load(myFile)

#removing all past predictions if they still exist in the predictions df
current_date = datetime.today().strftime('%Y-%m-%d')
final_date = datetime.now() + timedelta(days=10)
final_date = final_date.strftime('%Y-%m-%d')
print(current_date)
print(final_date)
for j in range(len(pl_pred)):
    game_date = pl_pred['Game Date'].loc[j]
    if game_date < current_date or game_date > final_date:
        pl_pred = pl_pred.drop([j], axis=0)
pl_pred = pl_pred.reset_index(drop=True)

pl_pred = pl_pred.drop('Venue', 1)
pl_pred = pl_pred.drop('Home Team Logo', 1)
pl_pred = pl_pred.drop('Away Team Logo', 1)
pl_pred = pl_pred.drop('Home Team ID', 1)
pl_pred = pl_pred.drop('Away Team ID', 1)
pl_pred = pl_pred.drop('index', 1)


pl_pred = pl_pred[["Game Date", "league", "Home Team", "Away Team", "Home Win", "Draw", "Away Win", "Fixture ID"]]
pl_pred = pl_pred.sort_values(by=['Game Date', 'league' ], ascending=(True,True))

pl_pred.to_excel(f'predictions_with_cuotes/lista_de_predicciones_{current_date}.xlsx', index=False)





print(pl_pred)
