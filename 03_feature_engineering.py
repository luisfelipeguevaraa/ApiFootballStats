# -*- coding: utf-8 -*-
"""
Created on Tue Nov 12 15:15:00 2021

@author: Luis Guevara
"""


print('\n\n ---------------- START ---------------- \n')

#-------------------------------- API-FOOTBALL --------------------------------

import time
start=time.time()

import pickle
import configparser

config = configparser.ConfigParser()
config.read('config.ini')
CODE_COUNTRY = config['DEFAULT']['CODE_COUNTRY']

from ml_functions.feature_engineering_functions import average_stats_df
from ml_functions.feature_engineering_functions import creating_ml_df


#------------------------------- INPUT VARIABLES ------------------------------

#Please state the name of the saved nested dictionary generated with '02_cleaning_stats_data.py', as well as the name of the saved output files (stats DataFrame).

stats_dict_saved_name = f'2019_2020_2021_{CODE_COUNTRY}_all_stats_dict.txt'

df_5_output_name = f'2019_2020_2021_{CODE_COUNTRY}_df_for_ml_5_v2.txt'
df_10_output_name = f'2019_2020_2021_{CODE_COUNTRY}_df_for_ml_10_v2.txt'


#----------------------------- FEATURE ENGINEERING ----------------------------

with open(f'clean_fixtures_and_dataframes/{CODE_COUNTRY}/{stats_dict_saved_name}', 'rb') as myFile:
    game_stats = pickle.load(myFile)

#creating a list with the team id in
team_list = []
for key in game_stats.keys():
    team_list.append(key)
team_list.sort()

#creating a dictionary with the team id as key and fixture id's as values
team_fixture_id_dict = {}
for team in team_list:
    fix_id_list = []
    for key in game_stats[team].keys():
        fix_id_list.append(key)
    fix_id_list.sort()
    sub_dict = {team:fix_id_list}
    team_fixture_id_dict.update(sub_dict)

#the list of fixtures was first home then away, we want them in chronological order so we need to sort them.
for team in team_fixture_id_dict:
    team_fixture_id_dict[team].sort()

#print(team_list)
#print(team_fixture_id_dict[33])
##print(game_stats)

#we can now iterate over the fixture ID list given a team id key using the dict created above. N.B./ the number of games over
# which the past data is averaged. A large number will smooth out past performance where as a small number will result
# in the prediction being heavily reliant on very recent form. This is worth testing the ml model build phase.

#5 game sliding average.
df_ml_5 = average_stats_df(5, team_list, team_fixture_id_dict, game_stats)
df_ml_5.to_csv(f'clean_fixtures_and_dataframes/{CODE_COUNTRY}/file_{CODE_COUNTRY}_2020_2021_df_ml_5.csv', index=False)
#print(df_ml_5)

#10 game sliding average.
df_ml_10 = average_stats_df(10, team_list, team_fixture_id_dict, game_stats)
df_ml_10.to_csv(f'clean_fixtures_and_dataframes/{CODE_COUNTRY}/file_{CODE_COUNTRY}_2020_2021_df_ml_10.csv', index=False)

#creating and saving the ml dataframe with a 5 game sliding average.
df_for_ml_5_v2 = creating_ml_df(df_ml_5)
with open(f'clean_fixtures_and_dataframes/{CODE_COUNTRY}/{df_5_output_name}', 'wb') as myFile:
    pickle.dump(df_for_ml_5_v2, myFile)

#creating and saving the ml dataframe with a 10 game sliding average.
df_for_ml_10_v2 = creating_ml_df(df_ml_10)
with open(f'clean_fixtures_and_dataframes/{CODE_COUNTRY}/{df_10_output_name}', 'wb') as myFile:
    pickle.dump(df_for_ml_10_v2, myFile)


df_for_ml_5_v2.to_csv(f'clean_fixtures_and_dataframes/{CODE_COUNTRY}/output_{CODE_COUNTRY}_2020_2021_df_ml_5.csv', index=False)
df_for_ml_10_v2.to_csv(f'clean_fixtures_and_dataframes/{CODE_COUNTRY}/output_{CODE_COUNTRY}_2020_2021_df_ml_10.csv', index=False)


# ----------------------------------- END -------------------------------------

print('\n', 'Script runtime:', round(((time.time()-start)/60), 2), 'minutes')
print(' ----------------- END ----------------- \n')
