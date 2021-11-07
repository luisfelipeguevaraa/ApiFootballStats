# -*- coding: utf-8 -*-
"""
Created on Sat Nov 06 20:31:13 2021

@author: Luis Guevara
"""


print('\n\n ---------------- START ---------------- \n')

#-------------------------------- API-FOOTBALL --------------------------------

import time
start=time.time()

import pandas as pd
import math
import pickle
import json



#------------------------------- INPUT VARIABLES ------------------------------

#Please state the name of the fixtures DataFrame we want to generate our dictionary,
# as well as the name of the saved output file (nested stats dictionary).

CODE_COUNTRY = 'de'

fixtures_saved_name = f'2019_2020_2021_{CODE_COUNTRY}_fixtures_df.csv'
stats_dict_output_name = f'2019_2020_2021_{CODE_COUNTRY}_all_stats_dict.txt'


#---------------------------- CREATING DF PER TEAM ----------------------------

#in this section we will create a nested dictionary containing the 20 teams, each with a value as another dictionary. In this dictionary we will have the game id along with the game dataframe.

fixtures_clean = pd.read_csv(f'clean_fixtures_and_dataframes/{CODE_COUNTRY}/{fixtures_saved_name}')

#creating the 'fixtures_clean' ID index which we will use to take data from this dataframe and add to each of our
# individual fixture stats dataframe.
fixtures_clean_ID_index = pd.Index(fixtures_clean['Fixture ID'])

#team id list that we can iterate over
team_id_list = (fixtures_clean['Home Team ID'].unique()).tolist()

#creating our dictionary which we will populate with data
all_stats_dict = {}

#nested for loop to create nested dictionary, first key by team id, second key by fixture id.
for team in team_id_list:

    #working the home teams
    team_fixture_list = []
    for i in fixtures_clean.index[:]:
        if fixtures_clean['Home Team ID'].iloc[i] == team:
            if math.isnan(fixtures_clean['Home Team Goals'].iloc[i]) == False:
                team_fixture_list.append(fixtures_clean['Fixture ID'].iloc[i])
    all_stats_dict[team] = {}
    for j in team_fixture_list:
        #loading df
        df = pd.read_json(f'game_stats_json_files/{CODE_COUNTRY}/' + str(j) + '.json', orient='values')
        #removing percentage symbol in possession and passes and conv to int
        df['Ball Possession'] = df['Ball Possession'].str.replace('[\%]', '', regex=True).astype(int)
        df['Passes %'] = df['Passes %'].str.replace('[\%]', '', regex=True).astype(int)
        #adding home vs away goals to df
        temp_index = fixtures_clean_ID_index.get_loc(j)
        home_goals = fixtures_clean['Home Team Goals'].iloc[temp_index]
        away_goals = fixtures_clean['Away Team Goals'].iloc[temp_index]
        df['Goals'] = [home_goals, away_goals]
        #adding points data
        if home_goals > away_goals:
            df['Points'] = [2,0]
        elif home_goals == away_goals:
            df['Points'] = [1,1]
        elif home_goals < away_goals:
            df['Points'] = [0,2]
        else:
            df['Points'] = ['nan', 'nan']
        #adding home-away identifier to df
        df['Team Identifier'] = [1,2]
        #adding team id
        df['Team ID'] = [team, fixtures_clean['Away Team ID'].iloc[temp_index]]
        #adding game date
        gd = fixtures_clean['Game Date'].iloc[temp_index]
        df['Game Date'] = [gd, gd]
        #adding this modified df to nested dictionary
        sub_dict_1 = {j:df}
        all_stats_dict[team].update(sub_dict_1)

    #working the away teams
    team_fixture_list = []
    for i in fixtures_clean.index[:]:
        if fixtures_clean['Away Team ID'].iloc[i] == team:
            if math.isnan(fixtures_clean['Away Team Goals'].iloc[i]) == False:
                team_fixture_list.append(fixtures_clean['Fixture ID'].iloc[i])
    for j in team_fixture_list:
        #loading df
        df = pd.read_json(f'game_stats_json_files/{CODE_COUNTRY}/' + str(j) + '.json', orient='values')
        #removing percentage symbol in possession and passes and conv to int
        df['Ball Possession'] = df['Ball Possession'].str.replace('[\%]', '', regex=True).astype(int)
        df['Passes %'] = df['Passes %'].str.replace('[\%]', '', regex=True).astype(int)
        #adding home vs away goals to df
        temp_index = fixtures_clean_ID_index.get_loc(j)
        home_goals = fixtures_clean['Home Team Goals'].iloc[temp_index]
        away_goals = fixtures_clean['Away Team Goals'].iloc[temp_index]
        df['Goals'] = [home_goals, away_goals]
        #adding points data
        if home_goals > away_goals:
            df['Points'] = [2,0]
        elif home_goals == away_goals:
            df['Points'] = [1,1]
        elif home_goals < away_goals:
            df['Points'] = [0,2]
        else:
            df['Points'] = ['nan', 'nan']
        #adding home-away identifier to df
        df['Team Identifier'] = [2,1]
        #adding team id
        df['Team ID'] = [fixtures_clean['Home Team ID'].iloc[temp_index], team]
        #adding game date
        gd = fixtures_clean['Game Date'].iloc[temp_index]
        df['Game Date'] = [gd, gd]
        #adding this modified df to nested dictionary
        sub_dict_1 = {j:df}
        all_stats_dict[team].update(sub_dict_1)

#saving our generated dictionary as a pickle file to import into a later python file.

with open(f'clean_fixtures_and_dataframes/{CODE_COUNTRY}/{stats_dict_output_name}', 'wb') as myFile:
    pickle.dump(all_stats_dict, myFile)

#with open(f'clean_fixtures_and_dataframes/{CODE_COUNTRY}/{stats_dict_output_name}', 'rb') as myFile:
    #loaded_dict_test = pickle.load(myFile)
    #print(loaded_dict_test[34][157023])
    #print(loaded_dict_test[42][157023])
    #loaded_dict_test[34][157023].to_csv('prem_clean_fixtures_and_dataframes/file_prem_2020_2021.csv', index=False)
    #for key, value in loaded_dict_test[34].items():
        #print(key)
        #print(key +"-"+str(value))
    #print(json.dumps(loaded_dict_test[34][157023], sort_keys=True, indent=4))


# ----------------------------------- END -------------------------------------

print('\n', 'Script runtime:', round(((time.time()-start)/60), 2), 'minutes')
print(' ----------------- END ----------------- \n')
