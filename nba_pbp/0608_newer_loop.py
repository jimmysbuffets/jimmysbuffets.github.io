import pandas as pd
from nba_api.stats.static import teams
teams_df = pd.DataFrame(teams.get_teams()).sort_values(by='full_name')

import numpy as np
import pandas as pd
from tqdm import trange

df_dict = {}
for row in teams_df.iloc[0:3].index:
    team_fullname = teams_df.loc[row, ['full_name']].item()
    team_abbrev = teams_df.loc[row, ['abbreviation']].item()

    game_stints_all = pd.DataFrame()
    team_id, games, team_roster = get_teamdata(team_fullname)

    for game_num in trange(1, 83):
        game_id = games.loc[games['GAME_NUM'] == game_num, 'GAME_ID'].item()
        game_hvv = games.loc[games['GAME_NUM'] == game_num, 'HvV'].item()

        pbp2_df = get_gamepbp(game_id, game_hvv)
        qs_dict = get_quarterstarters(pbp2_df)
        qs_checker(qs_dict)
        subs_df = get_subs(pbp2_df)
        game_stints_df = get_gamestints()

        game_stints_all = pd.concat([game_stints_all, game_stints_df])

    df_dict.update({f"{team_abbrev}_gamestints": game_stints_all})
